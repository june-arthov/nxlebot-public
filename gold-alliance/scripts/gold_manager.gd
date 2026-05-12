extends Node

var total_gold: int = 0
var session_gold: int = 0
var leaderboard: Array[Dictionary] = []

signal gold_changed(new_total: int, delta: int)
signal leaderboard_updated

func _ready() -> void:
	pass

func add_gold(amount: int, source: String = "") -> void:
	var clamped = maxi(amount, 0)
	total_gold += clamped
	session_gold += clamped
	gold_changed.emit(total_gold, clamped)
	print("[Gold] +", clamped, " from ", source, " | Total: ", total_gold)

func spend_gold(amount: int) -> bool:
	if amount > total_gold:
		return false
	total_gold -= amount
	gold_changed.emit(total_gold, -amount)
	return true

func get_total() -> int:
	return total_gold

func submit_leaderboard(name: String) -> void:
	var entry = {"name": name, "gold": session_gold, "time": Time.get_time_string_from_system()}
	leaderboard.append(entry)
	leaderboard.sort_custom(func(a, b): return a["gold"] > b["gold"])
	leaderboard_updated.emit()
