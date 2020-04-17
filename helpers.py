def get_board(boards, name):
    for board in boards:
        if board.name == name:
            return board
    return None

def get_list(lists, name):
    for item in lists:
        if item.name == name:
            return item
    return None