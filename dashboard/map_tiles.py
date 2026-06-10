import os

import folium


VWORLD_TILE_URL = "https://api.vworld.kr/req/wmts/1.0.0/{key}/Base/{z}/{y}/{x}.png"


def add_base_tiles(map_object):
    vworld_key = os.getenv("VWORLD_API_KEY")

    if vworld_key:
        folium.TileLayer(
            tiles=VWORLD_TILE_URL.format(key=vworld_key),
            attr="VWorld",
            name="국내 지도",
            overlay=False,
            control=False,
        ).add_to(map_object)
        return

    folium.TileLayer(
        tiles="OpenStreetMap",
        name="기본 지도",
        overlay=False,
        control=False,
    ).add_to(map_object)
