from time import time
from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.networks import AnyHttpUrl
from datetime import datetime

__all__ = ["user_info", "problem", "submission", "ratingch", "contest"]


class user_info(BaseModel):
    # User
    handle: str = Field(alias="handle")
    now_rating: int = Field(alias="rating")
    max_rating: int = Field(alias="maxRating")
    title_photo: AnyHttpUrl = Field(alias="titlePhoto")
    friends_count: int = Field(alias="friendOfCount")
    last_updated: int = Field(default_factory=time)


class author(BaseModel):
    contest_id: int = Field(alias="contestId")
    parti_type: str = Field(alias="participantType")

    class Config:
        extra = "ignore"


class problem(BaseModel):
    contest_id: int = Field(alias="contestId")
    problem_name: str = Field(alias="name")
    problem_index: str = Field(alias="index")
    problem_points: float = Field(alias="points", default=0)
    problem_rating: float = Field(alias="rating", default=0)

    class Config:
        extra = "ignore"


class submission(BaseModel):
    # BaseSubmission
    id: int = Field(alias="id")
    submission_time: int = Field(alias="creationTimeSeconds")
    contest_id: int = Field(alias="contestId")
    verdict: str = Field(alias="verdict")
    problem: problem
    author: author

    class Config:
        extra = "ignore"


class ratingch(BaseModel):

    handle: str = Field(alias="handle")
    contest_id: int = Field(alias="contestId")
    name: str = Field(alias="contestName")
    rank: int = Field(alias="rank")
    old_rating: int = Field(alias="oldRating")
    new_rating: int = Field(alias="newRating")
    time_second: int = Field(alias="ratingUpdateTimeSeconds")
    last_updated: int = Field(default_factory=time)

    class Config:
        extra = "ignore"


class contest(BaseModel):

    contest_id: int = Field(alias="id")
    name: str = Field(alias="name")
    start_time: int = Field(alias="startTimeSeconds")
    last_updated: int = Field(default_factory=time)

    class Config:
        extra = "ignore"
