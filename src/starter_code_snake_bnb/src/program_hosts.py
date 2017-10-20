from colorama import Fore
from infrastructure.switchlang import switch
import infrastructure.state as state
import services.data_service as svc
from dateutil import parser

def run():
    print(' ****************** Welcome host **************** ')
    print()

    show_commands()

    while True:
        action = get_action()

        with switch(action) as s:
            s.case('c', create_account)
            s.case('a', log_into_account)
            s.case('l', list_cages)
            s.case('r', register_cage)
            s.case('u', update_availability)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.default(unknown_command)

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[R]egister a cage')
    print('[U]pdate cage availability')
    print('[V]iew your bookings')
    print('Change [M]ode (guest or host)')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def create_account():
    print(' ****************** REGISTER **************** ')
    name = input("What is your name? ")
    email = input("What is your email? ").strip().lower()

    if (svc.find_account_by_email(email)):
        error_msg(f"This email ({email}) already exists.. ")
        return
    else:
        state.active_account = svc.create_account(name, email)



def log_into_account():
    print(' ****************** LOGIN **************** ')

    email = input("What is your email? ").strip().lower()
    account = svc.find_account_by_email(email)
    if not account:
        error_msg(f'Could not find account with email {email}.')
        return
    state.active_account = account
    success_msg('Logged in successfully.')

    


def register_cage():
    print(' ****************** REGISTER CAGE **************** ')

    if not state.active_account:
        error_msg("You must login first to register a cage.")
        return
    meters = input("How many square meters is the cage? ")
    if not meters:
        error_msg("Cancelled")
        return

    meters = float(meters)
    price = float(input("What is the price per night? "))
    carpeted = input("Is it carpeted [y, n]").lower().startswith("y")
    has_toys = input("Have snake toys [y, n]? ").lower().startswith("y")
    allow_dangerous = input("Can you host venomous snakes [y, n]").startswith('y')
    name = input("Give your cage a name: ")
    
    registered_cage = svc.register_cage(state.active_account,meters = meters, carpeted = carpeted, 
                        has_toys = has_toys, allow_dangerous = allow_dangerous, name= name, price= price)

    state.reload_account()
    success_msg(f"Registered new cage with id {registered_cage.id}")


def list_cages(supress_header=False):
    if not supress_header:
        print(' ******************     Your cages     **************** ')

    if not state.active_account:
        error_msg("You must login first to register a cage.")
        return
    cages = svc.find_cages_for_user(state.active_account)
    print(f"Found {len(cages)} Cages!")
    for idx, cage in enumerate(cages):
        print(f" {idx+1}, {cage.name} is {cage.square_meters} meters.")
        for booking in cage.bookings:
            print('     * Booking: {}, {} days, booked? {}'.format(
                booking.check_in_date,
                (booking.check_out_date - booking.check_in_date).days,
                'Yes' if booking.booked_date is not None else 'no'
            ))


def update_availability():
    print(' ****************** Add available date **************** ')

    if not state.active_account:
        error_msg("You must login first to register a cage.")
        return

    list_cages()

    cage_number = input("Enter the cage number: ")
    if not cage_number.strip():
        error_msg("Cancelled")
        print()
        return
    cage_number = int(cage_number)

    cages = svc.find_cages_for_user(state.active_account)
    selected_cage = cages[cage_number-1]

    start_date = parser.parse(
        input("Enter the start date [yyyy-mm-dd]: ")
    )
    days = int(input("Enter how many days for this stay? "))
    
    svc.add_available_date(
        selected_cage,
        start_date,
        days
    )

    state.reload_account()
    success_msg(f"Date added to cage {selected_cage.name}.")


def view_bookings():
    print(' ****************** Your bookings **************** ')

    # TODO: Require an account
    # TODO: Get cages, and nested bookings as flat list
    # TODO: Print details for each

    print(" -------- NOT IMPLEMENTED -------- ")


def exit_app():
    print()
    print('bye')
    raise KeyboardInterrupt()


def get_action():
    text = '> '
    if state.active_account:
        text = f'{state.active_account.name}> '

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def unknown_command():
    print("Sorry we didn't understand that command.")


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
