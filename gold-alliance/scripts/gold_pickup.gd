extends Area2D

@export var gold_value: int = 10
@export var bob_speed: float = 3.0
@export var bob_height: float = 5.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var collect_sound: AudioStreamPlayer = $CollectSound

var base_y: float = 0.0
var time: float = 0.0

func _ready() -> void:
	base_y = sprite.position.y
	body_entered.connect(_on_body_entered)

func _process(delta: float) -> void:
	time += delta * bob_speed
	sprite.position.y = base_y + sin(time) * bob_height

func _on_body_entered(body: Node2D) -> void:
	if body.has_method("collect_gold"):
		body.collect_gold(gold_value)
		collect_sound.play()
		sprite.visible = false
		await collect_sound.finished
		queue_free()
