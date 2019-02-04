data = {}


def setup():
    global data

    from .schema import Ship, Faction

    # Yeah, technically it's Corellian. But it flew in the service of the rebels,
    # so for the purposes of this demo it's a rebel ship.

    rebels = Faction(
        id="1", name="Alliance to Restore the Republic", ships=["1", "2", "3", "4", "5"],
    )

    empire = Faction(id="2", name="Galactic Empire", ships=["6", "7", "8"])

    data = {
        "Faction": {"1": rebels, "2": empire},
        "Ship": {
            "1": Ship(id="1", name="X-Wing"),
            "2": Ship(id="2", name="Y-Wing"),
            "3": Ship(id="3", name="A-Wing"),
            "4": Ship(id="4", name="Millenium Falcon"),
            "5": Ship(id="5", name="Home One"),
            "6": Ship(id="6", name="TIE Fighter"),
            "7": Ship(id="7", name="TIE Interceptor"),
            "8": Ship(id="8", name="Executor")
        },
    }

    data.update({
        "Users": [
            dict(name="Ge Yang", username="episodeyang"),
            dict(name="Amy Zhang", username="amyzhang"),
        ],
        "Teams": [
            dict(name="FAIR", username="fairinternal"),
            dict(name="Escher.ai", username="escher-ai"),
        ],
        "Projects": [
            dict(name="gmo-experiments", description="generalized metric optimization", ),
            dict(name="LeaF", description="Learning to Learn from Flawed Demonstrations", )
        ],
    })


def get_user(username, ):
    from .schema import User

    user = User(**data['Users'][0])
    return user


def create_ship(ship_name, faction_id):
    from .schema import Ship

    next_ship = len(data["Ship"].keys()) + 1
    new_ship = Ship(id=str(next_ship), name=ship_name)
    data["Ship"][new_ship.id] = new_ship
    data["Faction"][faction_id].ships.append(new_ship.id)
    return new_ship


def get_ship(_id):
    return data["Ship"][_id]


def get_faction(_id):
    return data["Faction"][_id]


def get_rebels():
    return get_faction("1")


def get_empire():
    return get_faction("2")
