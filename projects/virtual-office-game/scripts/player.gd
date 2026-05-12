extends CharacterBody2D

@export var speed: float = 200.0
@export var walk_animation_speed: float = 10.0

var current_animation = "idle"
var facing_direction = "right"

func _ready():
	# Set up collision layer
	collision_layer = 1
	collision_mask = 1
	
	# Connect to input events
	set_process_input(true)

func _physics_process(delta):
	var direction = Vector2.ZERO
	
	# Handle input
	if Input.is_action_pressed("move_left"):
		direction.x -= 1
		facing_direction = "left"
	if Input.is_action_pressed("move_right"):
		direction.x += 1
		facing_direction = "right"
	if Input.is_action_pressed("move_up"):
		direction.y -= 1
		facing_direction = "up"
	if Input.is_action_pressed("move_down"):
		direction.y += 1
		facing_direction = "down"
	
	# Normalize diagonal movement
	if direction.length() > 0:
		direction = direction.normalized()
	
	# Move the player
	velocity = direction * speed
	move_and_slide()
	
	# Update animation based on movement
	if direction.length() > 0:
		current_animation = "walk"
	else:
		current_animation = "idle"
	
	print("Player moving: ", direction, " Animation: ", current_animation)

func _input(event):
	# Handle object interaction
	if event.is_action_pressed("interact"):
		print("Interaction key pressed!")
		# TODO: Implement interaction logic
		check_for_interaction()

func check_for_interaction():
	# Check if player is near any interactable objects
	# TODO: Implement proximity detection and interaction
	print("Checking for nearby objects...")