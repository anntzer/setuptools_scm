import pytest
from setuptools_scm.config import Configuration
from setuptools_scm.version import (
    meta,
    simplified_semver_version,
    release_branch_semver_version,
    tags_to_versions,
    no_guess_dev_version,
    guess_next_version,
)


c = Configuration()


@pytest.mark.parametrize(
    "version, expected_next",
    [
        pytest.param(meta("1.0.0", config=c), "1.0.0", id="exact"),
        pytest.param(meta("1.0", config=c), "1.0.0", id="short_tag"),
        pytest.param(
            meta("1.0.0", distance=2, branch="default", config=c),
            "1.0.1.dev2",
            id="normal_branch",
        ),
        pytest.param(
            meta("1.0", distance=2, branch="default", config=c),
            "1.0.1.dev2",
            id="normal_branch_short_tag",
        ),
        pytest.param(
            meta("1.0.0", distance=2, branch="feature", config=c),
            "1.1.0.dev2",
            id="feature_branch",
        ),
        pytest.param(
            meta("1.0", distance=2, branch="feature", config=c),
            "1.1.0.dev2",
            id="feature_branch_short_tag",
        ),
        pytest.param(
            meta("1.0.0", distance=2, branch="features/test", config=c),
            "1.1.0.dev2",
            id="feature_in_branch",
        ),
    ],
)
def test_next_semver(version, expected_next):
    computed = simplified_semver_version(version)
    assert computed == expected_next


def test_next_semver_bad_tag():

    version = meta("1.0.0-foo", config=c)
    with pytest.raises(
        ValueError, match="1.0.0-foo can't be parsed as numeric version"
    ):
        simplified_semver_version(version)


@pytest.mark.parametrize(
    "version, expected_next",
    [
        pytest.param(meta("1.0.0", config=c), "1.0.0", id="exact"),
        pytest.param(
            meta("1.0.0", distance=2, branch="master", config=c),
            "1.1.0.dev2",
            id="development_branch",
        ),
        pytest.param(
            meta("1.0.0rc1", distance=2, branch="master", config=c),
            "1.1.0.dev2",
            id="development_branch_release_candidate",
        ),
        pytest.param(
            meta("1.0.0", distance=2, branch="maintenance/1.0.x", config=c),
            "1.0.1.dev2",
            id="release_branch_legacy_version",
        ),
        pytest.param(
            meta("1.0.0", distance=2, branch="release-1.0", config=c),
            "1.0.1.dev2",
            id="release_branch_with_prefix",
        ),
        pytest.param(
            meta("1.0.0", distance=2, branch="bugfix/3434", config=c),
            "1.1.0.dev2",
            id="false_positive_release_branch",
        ),
    ],
)
def test_next_release_branch_semver(version, expected_next):
    computed = release_branch_semver_version(version)
    assert computed == expected_next


@pytest.mark.parametrize(
    "version, expected_next",
    [
        pytest.param(
            meta("1.0.0", distance=2, branch="default", config=c),
            "1.0.0.post1.dev2",
            id="dev_distance",
        ),
        pytest.param(
            meta("1.0", distance=2, branch="default", config=c),
            "1.0.post1.dev2",
            id="dev_distance_short_tag",
        ),
        pytest.param(
            meta("1.0.0", distance=None, branch="default", config=c),
            "1.0.0",
            id="no_dev_distance",
        ),
    ],
)
def test_no_guess_version(version, expected_next):
    computed = no_guess_dev_version(version)
    assert computed == expected_next


def test_bump_dev_version_zero():
    guess_next_version("1.0.dev0")


def test_bump_dev_version_nonzero_raises():
    with pytest.raises(ValueError) as excinfo:
        guess_next_version("1.0.dev1")

    assert str(excinfo.value) == (
        "choosing custom numbers for the `.devX` distance "
        "is not supported.\n "
        "The 1.0.dev1 can't be bumped\n"
        "Please drop the tag or create a new supported one"
    )


@pytest.mark.parametrize(
    "tag, expected",
    [
        pytest.param("v1.0.0", "1.0.0"),
        pytest.param("v1.0.0-rc.1", "1.0.0rc1"),
        pytest.param("v1.0.0-rc.1+-25259o4382757gjurh54", "1.0.0rc1"),
    ],
)
def test_tag_regex1(tag, expected):
    if "+" in tag:
        # pytest bug wrt cardinality
        with pytest.warns(UserWarning):
            result = meta(tag, config=c)
    else:
        result = meta(tag, config=c)

    assert result.tag.public == expected


@pytest.mark.issue("https://github.com/pypa/setuptools_scm/issues/286")
def test_tags_to_versions():
    versions = tags_to_versions(["1.0", "2.0", "3.0"], config=c)
    assert isinstance(versions, list)  # enable subscription


@pytest.mark.issue("https://github.com/pypa/setuptools_scm/issues/471")
def test_version_bump_bad():
    with pytest.raises(
        ValueError,
        match=".*does not end with a number to bump, "
        "please correct or use a custom version scheme",
    ):

        guess_next_version(tag_version="2.0.0-alpha.5-PMC")
