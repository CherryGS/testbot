from time import time
from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.networks import AnyHttpUrl
from datetime import datetime


class user_info(BaseModel):
    # User
    handle: str = Field(alias="handle")
    now_rating: int = Field(alias="rating")
    max_rating: int = Field(alias="maxRating")
    title_photo: AnyHttpUrl = Field(alias="titlePhoto")
    friends_count: int = Field(alias="friendOfCount")
    last_updated: int = Field(default_factory=time)


class problem(BaseModel):
    contest_id: int = Field(alias="contestId")
    problem_name: str = Field(alias="name")
    problem_index: str = Field(alias="index")
    problem_points: float = Field(alias="points")
    problem_rating: float = Field(alias="rating")

    class Config:
        extra = "ignore"


class submission(BaseModel):
    # BaseSubmission
    id: int = Field(alias="id")
    submission_time: int = Field(alias="creationTimeSeconds")
    contest_id: int = Field(alias="contestId")
    verdict: str = Field(alias="verdict")
    problem: problem

    class Config:
        extra = "ignore"
