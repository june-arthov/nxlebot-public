extends Area2D

@export var direction: Vector2 = Vector2.RIGHT
@export var speed: float = 400.0
@export var damage: int = 15
@export var lifetime: float = 2.0

var shooter: Node2D = null

func _ready() -> void:
	await get_tree().create_timer(lifetime).timeout
	queue_free()

func _physics_process(delta: float) -> void:
	position += direction * speed * delta

func _on_body_entered(body: Node2D) -> void:
	if body == shooter:
		return
	if body.has_method("take_damage"):
		body.take_damage(damage)
		queue_free()
