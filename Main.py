import random, json

class HitLocation(object):
    def __init__(self, max_hp, rnd_part_hp):
        self.max_hp = max_hp
        self.rnd_part_hp = rnd_part_hp
        self.hp_coeff = 1.0

    def randomize_health(self, rand):
        min = 1.0 - self.rnd_part_hp
        max = 1.0 + self.rnd_part_hp
        self.hp_coeff = min + (max - min) * rand
        self.max_hp *= self.hp_coeff

    def __repr__(self):
        return 'max_hp: {}, hp_coeff: {}'.format(self.max_hp, self.hp_coeff)
        

def try_luck(vehicle_id, hit_locations):
    #save state
    _state = random.getstate()

    random.seed(vehicle_id)
    for hit_loc in hit_locations.values():
        hit_loc.randomize_health(random.random())

    #resore state
    random.setstate(_state)

    return hit_locations

def is_hitlocation(name, component):
    if isinstance(component, dict) and component.get('maxHP', None):
        return True
    if name.startswith('HP_'):
        for key in component:
            if key.startswith('HitLocation'):
                return True
    return False

def get_hitlocation(name, component):
    #hull hitlocations
    if isinstance(component, dict) and component.get('maxHP', None):
        name = '{}'.format(name)
        return (name, component)
    #other hitlocations
    if name.startswith('HP_'):
        for key in component:
            if key.startswith('HitLocation'):
                name = '{}.{}'.format(name, key)
                return (name, component[key])
    return None

def get_components(ship):
    hulls = [comp for comp_name, comp in ship['ShipUpgradeInfo'].iteritems() if comp_name[2:4] == 'UH']
    engines = [comp for comp_name, comp in ship['ShipUpgradeInfo'].iteritems() if comp_name[2:4] == 'UE']
    hulls[-1]['components']['engine'] = engines[-1]['components']['engine']
    return hulls[-1]['components']

def get_hitlocations(ship):
    hit_locations = {}
    components = get_components(ship)

    for comps in components.itervalues():
        if len(comps) >= 1:
            comp_name = comps[-1]
        else:
            continue

        for module_name, module in ship[comp_name].iteritems():
            hit_loc = get_hitlocation(module_name, module)
            if hit_loc is None:
                continue

            name, hl = hit_loc

            hit_locations[name] = HitLocation(hl['maxHP'], hl['rndPartHP'])

    return hit_locations


SHIP_NAME = 'PRSC610_Smolensk'
ENTITY_ID = 405147

def main():
    filename = 'Ship\\{}.json'.format(SHIP_NAME)
    with open(filename, 'r') as f:
        ship = json.load(f)

    hit_locations = get_hitlocations(ship)

    try_luck(ENTITY_ID, hit_locations)

    for hl_name, hl in hit_locations.items():
        print(hl_name, hl)

if __name__ == '__main__':
    main()