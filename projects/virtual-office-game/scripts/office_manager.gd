extends Node2D

@onready var player = $Office/Player
@onready var camera = $Office/Player/Camera2D

var game_state = {
	"player_position": Vector2.ZERO,
	"current_task": "none",
	"completed_tasks": [],
	"energy": 100,
	"morale": 75,
	"money": 0
}

var tasks = {
	"check_email": {
		"name": "Check Email",
		"description": "Read and respond to important emails",
		"energy_cost": 5,
		"reward": 10,
		"completed": false
	},
	"team_meeting": {
		"name": "Team Meeting",
		"description": "Attend daily standup meeting",
		"energy_cost": 10,
		"reward": 15,
		"completed": false
	},
	"code_review": {
		"name": "Code Review",
		"description": "Review pull requests from team",
		"energy_cost": 15,
		"reward": 20,
		"completed": false
	},
	"coffee_break": {
		"name": "Coffee Break",
		"description": "Take a coffee break to recharge",
		"energy_cost": -10,
		"reward": 5,
		"completed": false
	}
}

var npcs = []

func _ready():
	print("Virtual Office 2D - Game Starting!")
	initialize_game()
	setup_camera_limits()

func _process(delta):
	update_player_position()
	handle_game_loop()

func initialize_game():
	# Initialize game state
	print("Initializing game state...")
	game_state["player_position"] = player.global_position
	
	# Create NPCs
	create_npcs()
	
	# Setup input actions
	setup_input_actions()

func setup_camera_limits():
	# Set camera limits to prevent scrolling outside office
	camera.limit_left = 0
	camera.limit_right = 1024
	camera.limit_top = 0
	camera.limit_bottom = 768

func setup_input_actions():
	# This would normally be done in the project settings
	# For now, we'll handle it in the player script
	pass

func create_npcs():
	# Create NPCs around the office
	var npc_data = [
		{"name": "Alice", "position": Vector2(350, 250), "role": "Developer"},
		{"name": "Bob", "position": Vector2(650, 250), "role": "Designer"},
		{"name": "Carol", "position": Vector2(900, 450), "role": "Manager"}
	]
	
	for npc_info in npc_data:
		var npc = create_npc(npc_info)
		npcs.append(npc)

func create_npc(info):
	# TODO: Implement NPC creation
	print("Creating NPC: ", info["name"])
	return {"name": info["name"], "position": info["position"], "role": info["role"]}

func update_player_position():
	game_state["player_position"] = player.global_position

func handle_game_loop():
	# Handle game logic here
	# Energy depletion over time
	game_state["energy"] -= 0.1
	
	# Update morale based on energy
	if game_state["energy"] < 30:
		game_state["morale"] -= 0.2
	elif game_state["energy"] > 70:
		game_state["morale"] += 0.1
	
	# Clamp values
	game_state["energy"] = clamp(game_state["energy"], 0, 100)
	game_state["morale"] = clamp(game_state["morale"], 0, 100)
	
	print("Game State: Energy=", game_state["energy"], " Morale=", game_state["morale"])

func start_task(task_name):
	if task_name in tasks:
		var task = tasks[task_name]
		if game_state["energy"] >= task["energy_cost"]:
			game_state["current_task"] = task_name
			print("Starting task: ", task["name"])
		else:
			print("Not enough energy for task: ", task["name"])
	else:
		print("Task not found: ", task_name)

func complete_task(task_name):
	if task_name in tasks and not tasks[task_name]["completed"]:
		var task = tasks[task_name]
		game_state["energy"] += task["energy_cost"]
		game_state["money"] += task["reward"]
		tasks[task_name]["completed"] = true
		game_state["completed_tasks"].append(task_name)
		
		print("Task completed: ", task["name"])
		print("Reward: ", task["reward"], " money")
		
		# Reset current task
		game_state["current_task"] = "none"
	else:
		print("Task already completed or not found")