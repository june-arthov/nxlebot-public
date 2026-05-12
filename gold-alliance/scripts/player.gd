extends CharacterBody2D

@export var base_speed: float = 200.0
@export var sprint_multiplier: float = 1.8
@export var health: int = 100
@export var max_health: int = 100
@export var player_name: String = "Player"
@export var alliance_tag: String = ""

@onready var sprite: Sprite2D = $Sprite2D
@onready var animation_player: AnimationPlayer = $AnimationPlayer
@onready var shoot_cooldown: Timer = $ShootCooldown
@onready var melee_cooldown: Timer = $MeleeCooldown
@onready var camera: Camera2D = $Camera2D

const PROJECTILE_SCENE = preload("res://scenes/projectile.tscn")

var is_sprinting: bool = false
var facing: Vector2 = Vector2.RIGHT
var can_shoot: bool = true
var can_melee: bool = true
var is_dead: bool = false

signal health_changed(current: int, max_h: int)
signal died
signal gold_picked_up(amount: int)

func _ready() -> void:
	camera.make_current()
	health_changed.emit(health, max_health)

func _physics_process(delta: float) -> void:
	if is_dead:
		return
	
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	is_sprinting = Input.is_action_pressed("sprint") and direction != Vector2.ZERO
	
	var speed = base_speed * (sprint_multiplier if is_sprinting else 1.0)
	velocity = direction * speed
	
	if direction != Vector2.ZERO:
		facing = direction.normalized()
		animation_player.play("run")
		sprite.flip_h = direction.x < 0
	else:
		animation_player.play("idle")
		velocity = Vector2.ZERO
	
	move_and_slide()

func _input(event: InputEvent) -> void:
	if is_dead:
		return
	if event.is_action_pressed("shoot"):
		_shoot()
	if event.is_action_pressed("melee"):
		_melee()
	if event.is_action_pressed("interact"):
		_interact()
	if event.is_action_pressed("open_alliance"):
		_open_alliance_menu()

func _shoot() -> void:
	if not can_shoot:
		return
	can_shoot = false
	shoot_cooldown.start()
	
	var projectile = PROJECTILE_SCENE.instantiate()
	projectile.global_position = global_position + facing * 20
	projectile.direction = facing
	projectile.shooter = self
	get_tree().current_scene.add_child(projectile)
	
	animation_player.play("shoot")

func _melee() -> void:
	if not can_melee:
		return
	can_melee = false
	melee_cooldown.start()
	animation_player.play("melee")
	
	var query = PhysicsShapeQueryParameters2D.new()
	var circle = CircleShape2D.new()
	circle.radius = 40
	query.shape = circle
	query.transform = global_transform
	query.collision_mask = 2  # player layer
	
	var results = get_world_2d().direct_space_state.intersect_shape(query, 8)
	for result in results:
		var body = result["collider"]
		if body != self and body.has_method("take_damage"):
			body.take_damage(25)

func _interact() -> void:
	var query = PhysicsShapeQueryParameters2D.new()
	var circle = CircleShape2D.new()
	circle.radius = 50
	query.shape = circle
	query.transform = global_transform
	query.collision_mask = (1 << 5) | (1 << 6)  # portal + interactable
	
	var results = get_world_2d().direct_space_state.intersect_shape(query, 4)
	for result in results:
		var body = result["collider"]
		if body.has_method("interact"):
			body.interact(self)
			return

func _open_alliance_menu() -> void:
	# UI overlay handled by HUD
	pass

func take_damage(amount: int) -> void:
	if is_dead:
		return
	health -= amount
	health_changed.emit(health, max_health)
	animation_player.play("hurt")
	
	if health <= 0:
		_die()

func heal(amount: int) -> void:
	health = mini(health + amount, max_health)
	health_changed.emit(health, max_health)

func _die() -> void:
	is_dead = true
	velocity = Vector2.ZERO
	animation_player.play("die")
	died.emit()
	# Drop 50% gold
	GoldManager.spend_gold(GoldManager.get_total() / 2)
	# Respawn after 3s
	await get_tree().create_timer(3.0).timeout
	_respawn()

func _respawn() -> void:
	is_dead = false
	health = max_health
	health_changed.emit(health, max_health)
	global_position = Vector2.ZERO
	animation_player.play("idle")

func _on_shoot_cooldown_timeout() -> void:
	can_shoot = true

func _on_melee_cooldown_timeout() -> void:
	can_melee = true

func collect_gold(amount: int) -> void:
	GoldManager.add_gold(amount, "pickup")
	gold_picked_up.emit(amount)
