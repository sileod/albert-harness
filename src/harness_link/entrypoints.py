import sys

from . import cli, hlink as hlink_cli, spawn


def harness_link():
    cli.main()


def hlink():
    hlink_cli.main()


def harness_link_spawn():
    spawn.main()


def _provider(slug):
    cli.main([slug, *sys.argv[1:]])


def _provider_spawn(slug):
    spawn.main([slug, *sys.argv[1:]])


def albert():
    _provider("albert")


def nim():
    _provider("nim")


def orfree():
    _provider("orfree")


def albert_spawn():
    _provider_spawn("albert")


def nim_spawn():
    _provider_spawn("nim")


def orfree_spawn():
    _provider_spawn("orfree")
