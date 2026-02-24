def ghost_warning(ghost):
    if ghost.x < 300:
        ghost.opacity = 0.6
    else:
        ghost.opacity = 1