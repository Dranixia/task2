"""
Butynets' Danylo
"""

import folium
from geopy import distance


def movies_read(path):
    """
    (string) -> set
    Return all the necessary information about all movies in a form of set.
    """
    unique_movie_and_loc = set()
    with open(path, mode='r', errors='ignore', encoding='utf-8') as file:
        for line in file.readlines():
            try:
                line = line.strip()
                year = year_read(line)
                if year == '????':
                    continue
                name = name_read(line)
                place = place_read(line)
                unique_movie_and_loc.add((name, year, place))
            except IndexError:
                continue
    return unique_movie_and_loc


def name_read(string):
    """
    (string) -> string
    Return name of the movie from string.
    """
    return string.split(' (')[0].replace('"', '')


def year_read(string):
    """
    (string) -> string
    Return year the movie from string was filmed.
    """
    string = string.split(')')[0]
    if '/' in string[-4:]:
        return string.split('/')[0][-4:]
    return string.split(')')[0][-4:]


def place_read(string):
    """
    (string) -> string
    Return location the movie was filmed.
    """
    try:
        left_brace = string.index('{')
        right_brace = string.index('}')
        string = string.replace(string[left_brace:right_brace + 1], '')
    except ValueError:
        pass
    string = string.split('\t')
    for part in range(len(string)):
        if '(' in string[part] and part != 0:
            return string[-2]
        if ',' in string[part] and part != 0:
            return string[part]
    return string[-1]


def coordinates(path):
    """
    (string) -> set
    Return a set of tuples, where a single tuple
    is the name of city and its location in coordinates.
    """
    unique_cities = set()
    with open(path, mode='r', errors='ignore', encoding='utf-8') as file:
        file.readline()
        for line in file.readlines():
            line = line.strip().split('\t')[1:]
            unique_cities.add(tuple(line))
    return unique_cities


def sorting_by_year(full_set, req_year):
    """
    (set, str) -> set
    Return set with movies which were filmed in the year mentioned.
    """
    only_needed = set()
    for film in full_set:
        if film[1] == req_year:
            only_needed.add(film)
    return only_needed


def dct_creator(needed, locations):
    """
    (set, set) -> dict
    Return a dict where a key is coordinate and values are all movies filmed there.
    """
    places = dict()
    for loc in locations:
        for films in needed:
            if loc[0] in films[2]:
                if (loc[1], loc[2]) not in places:
                    places[(loc[1], loc[2])] = set()
                    places[(loc[1], loc[2])].add(films[0])
                elif (loc[1], loc[2]) in places:
                    places[(loc[1], loc[2])].add(films[0])
    return places


def loc_comparison(personal, other_locations, num):
    """
    (tuple, list, int) -> dict
    Return the closest n(num) coordinates to your desired point.
    """
    distances = dict()
    distances_list = []
    for location in other_locations:
        dist = distance.distance(personal, location).miles
        distances[dist] = location
        distances_list.append(dist)
    distances_list.sort()
    distances_list = distances_list[0:num]
    closest = {}
    for loc in distances:
        if loc in distances_list:
            closest[loc] = distances[loc]
    return closest


def suitable_films(places, films):
    """
    (dict, dict) -> dict
    Return a dict where keys are coordinates and values are
    movies filmed there.
    """
    suitable_dict = dict()
    for coordinate in films:
        if coordinate in places.values():
            suitable_dict[coordinate] = films[coordinate]
    return suitable_dict


def capitals_info(path):
    """
    (str) ->
    Return info about capitals of the world.
    """
    cap_info = dict()
    with open(path, mode='r', errors='ignore', encoding='utf-8') as file:
        file.readline()
        for line in file.readlines():
            line = line.strip().split(',')
            cap_info[(line[0], line[1])] = (line[2], line[3])
    return cap_info


def folium_markers(info, capital, starting_point):
    """
    (dict, dict, tuple) -> None
    Create html map with markers from given information.
    """
    for key in info:
        info[key] = list(info[key])[0]

    html_map = folium.Map(location=[starting_point[0], starting_point[1]],
                          zoom_start=12)
    user_layer = folium.FeatureGroup('User Location')
    user_layer.add_child(folium.Marker(location=starting_point,
                                       popup='Your chosen point is here.',
                                       icon=folium.Icon(color='red', icon='info-sign')))

    films_layer = folium.FeatureGroup('Closest film locations')

    for loc in info:
        films_layer.add_child(folium.Marker(location=loc,
                                            popup=str('Film:' + info[loc]),
                                            icon=folium.Icon(color='blue', icon='info-sign')))

    capital_layer = folium.FeatureGroup('Capitals of the World')

    for name in capital:
        capital_layer.add_child(folium.Marker(location=capital[name],
                                              popup="Country:" + str(name[0]) +
                                                    " City:" + str(name[1]),
                                              icon=folium.Icon(color='lightblue', icon='info-sign')))

    html_map.add_child(user_layer)
    html_map.add_child(films_layer)
    html_map.add_child(capital_layer)
    html_map.add_child(folium.LayerControl())
    html_map.save("map.html")
    print("Finished. Please have look at the: map.html")


def main():
    """
    (None) -> None
    Main function to make other functions interact.
    """
    year = input('Please, enter a year you would like to have a map for: ')
    my_lat = float(input('Enter your latitude: '))
    my_lon = float(input('Enter your longitude: '))
    my_loc = (my_lat, my_lon)

    num_of_films = int(input('Enter the number of closest film locations(max 10): '))
    while num_of_films not in range(1, 11):
        num_of_films = int(input('Enter the number of closest film locations(max 10): '))

    print('Map is generating...')
    print('Please wait...')

    everything_movie = movies_read('locations.list')
    coords = coordinates('city_coordinates.tsv')
    cap_inf = capitals_info('task2/capitals.txt')
    req_movies = sorting_by_year(everything_movie, year)
    places_and_names = dct_creator(req_movies, coords)
    locations = loc_comparison(my_loc, places_and_names.keys(), num_of_films)
    suitable_dict = suitable_films(locations, places_and_names)
    folium_markers(suitable_dict, cap_inf, my_loc)


if __name__ == '__main__':
    main()
