# from pymongo.operations import UpdateMany
# from rich.console import Console

# from server.utils import mana_value
# from server.db import get_database

# console = Console()


# def create_update(mana_cost: str) -> UpdateMany:
#     return UpdateMany(
#         { 'mana_cost': mana_cost },
#         [{ '$set': { 'mana_value': mana_value(mana_cost) } }]
#     )


# def main():
#     console.print('MtG Card Data - Add Mana Value')
#     db = get_database()

#     with console.status('Fetching Distinct Mana Costs'):
#         distinct_mana_costs = db['cards'].distinct('mana_cost')
    
#     with console.status('Processing Mana Values...'):
#         updates = [create_update(c) for c in distinct_mana_costs if c]

#     with console.status('Applying bulk update'):
#         with get_client() as client:
#         db['cards'].bulk_write(updates)


# if __name__ == '__main__':
#     main()
