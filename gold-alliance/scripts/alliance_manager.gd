extends Node

var members: Array[String] = []
var alliance_tag: String = ""
var shared_loot_percent: float = 0.1  # 10% shared to alliance

signal member_joined(name: String)
signal member_left(name: String)
signal alliance_tag_changed(tag: String)

func create_alliance(tag: String) -> void:
	alliance_tag = tag
	members.clear()
	alliance_tag_changed.emit(tag)

func invite_player(player_name: String) -> bool:
	if members.has(player_name):
		return false
	members.append(player_name)
	member_joined.emit(player_name)
	return true

func kick_player(player_name: String) -> bool:
	var idx = members.find(player_name)
	if idx == -1:
		return false
	members.remove_at(idx)
	member_left.emit(player_name)
	return true

func get_members() -> Array[String]:
	return members.duplicate()

func get_tag() -> String:
	return alliance_tag

func calculate_share(personal_loot: int) -> int:
	return int(personal_loot * shared_loot_percent)
