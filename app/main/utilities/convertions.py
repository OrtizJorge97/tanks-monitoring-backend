def convert_tank_parameters(tank_parameters):
    tank_parameters_list = []
    for tank_parameter in tank_parameters:
        tank_parameter_dictionary = {
            "tankId": tank_parameter[0],
            "parameter": tank_parameter[1],
            "tankMinValue": tank_parameter[2],
            "tankMaxValue": tank_parameter[3]
        }
        tank_parameters_list.append(tank_parameter_dictionary)

    return tank_parameters_list
