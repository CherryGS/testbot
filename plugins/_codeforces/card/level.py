from typing import List, Tuple, Type

# TODO : 采用更好的方案


class role:
    rating: Tuple[int, int]
    color: List[str]


class newbie(role):
    rating = (0, 1200)
    color = ["#cccccc"]


class pupil(role):
    rating = (1200, 1400)
    color = ["#8cfe71"]


class specialist(role):
    rating = (1400, 1600)
    color = ["#86ddba"]


class expert(role):
    rating = (1600, 1900)
    color = ["#acaaff"]


class candidateMaster(role):
    rating = (1900, 2100)
    color = ["#f78aff"]


class master(role):
    rating = (2100, 2300)
    color = ["#facc86"]


class internationalMaster(role):
    rating = (2300, 2400)
    color = ["#f8bb52"]


class grandmaster(role):
    rating = (2400, 2600)
    color = ["#f57877"]


class internationalGrandmaster(role):
    rating = (2600, 3000)
    color = ["#f33734"]


class legendaryGrandmaster(role):
    rating = (3000, 10000)
    color = ["#000000", "#a10703"]


async def check_rating(rating: int) -> Type[role]:
    if rating < 1200:
        return newbie
    elif rating < 1400:
        return pupil
    elif rating < 1600:
        return specialist
    elif rating < 1900:
        return expert
    elif rating < 2100:
        return candidateMaster
    elif rating < 2300:
        return master
    elif rating < 2400:
        return internationalMaster
    elif rating < 2600:
        return grandmaster
    elif rating < 3000:
        return internationalGrandmaster
    elif rating < 4000:
        return legendaryGrandmaster
    else:
        raise ValueError("rating out of range")
