import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


class InvalidDateException(Exception):
    """Exception raised when an invalid date is provided."""

    pass


def validate_date(date_str):
    """Validates if the date is in the format dd-mm-yyyy."""
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        raise InvalidDateException(
            "Invalid date. Use the format dd-mm-yyyy."
        )


class Customer:
    """Represents a customer in the banking system."""

    def __init__(self, address):
        """Initializes a new customer.

        Args:
            address (str): The customer's address.
        """
        self.address = address
        self.accounts = []

    def make_transaction(self, account, transaction):
        """Performs a transaction on a specific account.

        Args:
            account (Account): The account on which the transaction will be performed.
            transaction (Transaction): The transaction to be performed.
        """
        transaction.register(account)

    def add_account(self, account):
        """Adds an account to the customer's account list.

        Args:
            account (Account): The account to be added.
        """
        self.accounts.append(account)


class IndividualCustomer(Customer):
    """Represents an individual as a customer."""

    def __init__(self, name, date_of_birth, ssn, address):
        """Initializes a new individual customer.

        Args:
            name (str): The person's full name.
            date_of_birth (str): The date of birth in dd-mm-yyyy format.
            ssn (str): The person's Social Security Number.
            address (str): The person's address.
        
        Raises:
            InvalidDateException: If the date of birth is not in the correct format.
        """
        super().__init__(address)
        self.name = name
        validate_date(date_of_birth)  # Validates the date of birth
        self.date_of_birth = date_of_birth
        self.ssn = ssn


class Account:
    """Represents a bank account."""

    def __init__(self, number, customer):
        """Initializes a new account.

        Args:
            number (int): The account number.
            customer (Customer): The account holder.
        """
        self._balance = 0
        self._number = number
        self._branch = "0001"
        self._customer = customer
        self._history = TransactionHistory()

    @classmethod
    def new_account(cls, customer, number):
        """Creates a new instance of the Account class.

        Args:
            customer (Customer): The account holder.
            number (int): The account number.

        Returns:
            Account: The new account instance.
        """
        return cls(number, customer)

    @property
    def balance(self):
        """float: The current account balance."""
        return self._balance

    @property
    def number(self):
        """int: The account number."""
        return self._number

    @property
    def branch(self):
        """str: The account's branch."""
        return self._branch

    @property
    def customer(self):
        """Customer: The account holder."""
        return self._customer

    @property
    def history(self):
        """TransactionHistory: The account's transaction history."""
        return self._history

    def withdraw(self, amount):
        """Withdraws money from the account.

        Args:
            amount (float): The amount to be withdrawn.

        Returns:
            bool: True if the withdrawal is successful, False otherwise.
        """
        balance = self.balance
        insufficient_funds = amount > balance

        if insufficient_funds:
            print("\n@@@ Operation failed! Insufficient funds. @@@")

        elif amount > 0:
            self._balance -= amount
            print("\n=== Withdrawal successful! ===")
            return True

        else:
            print("\n@@@ Operation failed! Invalid amount. @@@")

        return False

    def deposit(self, amount):
        """Deposits money into the account.

        Args:
            amount (float): The amount to be deposited.

        Returns:
            bool: True if the deposit is successful, False otherwise.
        """
        if amount > 0:
            self._balance += amount
            print("\n=== Deposit successful! ===")
            return True
        else:
            print("\n@@@ Operation failed! Invalid amount. @@@")
            return False


class CheckingAccount(Account):
    """Represents a checking account, with withdrawal limits."""

    def __init__(self, number, customer, limit=500, withdrawal_limit=3):
        """Initializes a new checking account.

        Args:
            number (int): The account number.
            customer (Customer): The account holder.
            limit (float, optional): The account credit limit. Defaults to 500.
            withdrawal_limit (int, optional): The daily withdrawal limit. Defaults to 3.
        """
        super().__init__(number, customer)
        self._limit = limit
        self._withdrawal_limit = withdrawal_limit

    def withdraw(self, amount):
        """Withdraws money from the checking account, checking for limits.

        Args:
            amount (float): The amount to be withdrawn.

        Returns:
            bool: True if the withdrawal is successful, False otherwise.
        """
        number_withdrawals = len(
            [
                transaction
                for transaction in self.history.transactions
                if transaction["type"] == Withdrawal.__name__
            ]
        )

        exceeded_limit = amount > self._limit
        exceeded_withdrawals = number_withdrawals >= self._withdrawal_limit

        if exceeded_limit:
            print("\n@@@ Operation failed! Withdrawal amount exceeds the limit. @@@")

        elif exceeded_withdrawals:
            print("\n@@@ Operation failed! Maximum number of withdrawals exceeded. @@@")

        else:
            return super().withdraw(amount)

        return False

    def __str__(self):
        """Returns a string representation of the checking account."""
        return f"""\
            Branch:\t{self.branch}
            Account:\t{self.number}
            Holder:\t{self.customer.name}
        """


class TransactionHistory:
    """Stores the transaction history of an account."""

    def __init__(self):
        """Initializes a new transaction history."""
        self._transactions = []

    @property
    def transactions(self):
        """list: The list of transactions in the history."""
        return self._transactions

    def add_transaction(self, transaction):
        """Adds a transaction to the history.

        Args:
            transaction (Transaction): The transaction to be added.
        """
        self._transactions.append(
            {
                "type": transaction.__class__.__name__,
                "amount": transaction.amount,
                "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Transaction(ABC):
    """Abstract base class to represent banking transactions."""

    @property
    @abstractproperty
    def amount(self):
        """float: The transaction amount."""
        pass

    @abstractclassmethod
    def register(self, account):
        """Registers the transaction on an account.

        Args:
            account (Account): The account on which to register the transaction.
        """
        pass


class Withdrawal(Transaction):
    """Represents a withdrawal transaction."""

    def __init__(self, amount):
        """Initializes a new withdrawal.

        Args:
            amount (float): The amount to be withdrawn.
        """
        self._amount = amount

    @property
    def amount(self):
        """float: The withdrawal amount."""
        return self._amount

    def register(self, account):
        """Registers the withdrawal in the account if successful.

        Args:
            account (Account): The account from which the money will be withdrawn.
        """
        transaction_success = account.withdraw(self.amount)

        if transaction_success:
            account.history.add_transaction(self)


class Deposit(Transaction):
    """Represents a deposit transaction."""

    def __init__(self, amount):
        """Initializes a new deposit.

        Args:
            amount (float): The amount to be deposited.
        """
        self._amount = amount

    @property
    def amount(self):
        """float: The deposit amount."""
        return self._amount

    def register(self, account):
        """Registers the deposit in the account if successful.

        Args:
            account (Account): The account into which the money will be deposited.
        """
        transaction_success = account.deposit(self.amount)

        if transaction_success:
            account.history.add_transaction(self)


def menu():
    """Displays the banking system options menu.

    Returns:
        str: The option selected by the user.
    """
    menu = """\n
    ================ MENU ================
    [1]\tDeposit
    [2]\tWithdraw
    [3]\tStatement
    [4]\tNew Account
    [5]\tList Accounts
    [6]\tNew Customer
    [7]\tExit
    => """
    return input(textwrap.dedent(menu))


def filter_customer(ssn, customers):
    """Filters a customer from the customer list based on SSN.

    Args:
        ssn (str): The SSN of the customer to be filtered.
        customers (list): The list of customers.

    Returns:
        Customer: The found customer or None if the SSN is not found.
    """
    filtered_customers = [customer for customer in customers if customer.ssn == ssn]
    return filtered_customers[0] if filtered_customers else None


def get_account(customers):
    """Gets an account from a customer, allowing selection among multiple accounts.

    Args:
        customers (list): The customer list.

    Returns:
        Account: The account selected by the user or None if it's not possible to get the account.
    """
    ssn = input("Enter the customer's SSN: ")
    customer = filter_customer(ssn, customers)

    if not customer:
        print("\n@@@ Customer not found! @@@")
        return None

    if not customer.accounts:
        print("\n@@@ Customer has no account! @@@")
        return None

    if len(customer.accounts) == 1:
        return customer.accounts[0]

    print("\n=== Customer Accounts: ===")
    for i, account in enumerate(customer.accounts):
        print(f"[{i + 1}] Branch: {account.branch}, Number: {account.number}")

    while True:
        try:
            account_option = int(input("Select the desired account: "))
            if 1 <= account_option <= len(customer.accounts):
                return customer.accounts[account_option - 1]
            else:
                print("\n@@@ Invalid option! @@@")
        except ValueError:
            print("\n@@@ Invalid input. Enter a number. @@@")


def deposit(customers):
    """Makes a deposit into a customer's account.

    Args:
        customers (list): The customer list.
    """
    account = get_account(customers)
    if not account:
        return

    while True:
        try:
            amount = float(input("Enter the deposit amount: "))
            if amount > 0:
                transaction = Deposit(amount)
                account.customer.make_transaction(account, transaction)
                break
            else:
                print(
                    "\n@@@ Operation failed! The deposit amount must be positive. @@@"
                )
        except ValueError:
            print("\n@@@ Invalid input. Enter a number. @@@")


def withdraw(customers):
    """Makes a withdrawal from a customer's account.

    Args:
        customers (list): The customer list.
    """
    account = get_account(customers)
    if not account:
        return

    while True:
        try:
            amount = float(input("Enter the withdrawal amount: "))
            if amount > 0:
                transaction = Withdrawal(amount)
                account.customer.make_transaction(account, transaction)
                break
            else:
                print(
                    "\n@@@ Operation failed! The withdrawal amount must be positive. @@@"
                )
        except ValueError:
            print("\n@@@ Invalid input. Enter a number. @@@")


def display_statement(customers):
    """Displays a customer's account statement.

    Args:
        customers (list): The customer list.
    """
    account = get_account(customers)
    if not account:
        return

    print("\n================ STATEMENT ================")
    transactions = account.history.transactions

    statement = ""
    if not transactions:
        statement = "No transactions have been made."
    else:
        for transaction in transactions:
            statement += f"\n{transaction['type']}:\n\t$ {transaction['amount']:.2f}\n\tDate: {transaction['date']}"

    print(statement)
    print(f"\nBalance:\n\t$ {account.balance:.2f}")
    print("==========================================")


def create_customer(customers):
    """Creates a new customer in the system.

    Args:
        customers (list): The customer list.
    """
    ssn = input("Enter the SSN (numbers only): ")
    customer = filter_customer(ssn, customers)

    if customer:
        print("\n@@@ A customer with this SSN already exists! @@@")
        return

    name = input("Enter the full name: ")
    while True:  # Loop to ensure valid date
        try:
            date_of_birth = input("Enter the date of birth (dd-mm-yyyy): ")
            validate_date(date_of_birth)
            break
        except InvalidDateException as e:
            print(f"\n@@@ {e} @@@")
    address = input(
        "Enter the address (street, number - neighborhood - city/state abbreviation): "
    )

    customer = IndividualCustomer(
        name=name, date_of_birth=date_of_birth, ssn=ssn, address=address
    )

    customers.append(customer)

    print("\n=== Customer created successfully! ===")


def create_account(account_number, customers, accounts):
    """Creates a new account for an existing customer.

    Args:
        account_number (int): The account number to be created.
        customers (list): The customer list.
        accounts (list): The account list.
    """
    ssn = input("Enter the customer's SSN: ")
    customer = filter_customer(ssn, customers)

    if not customer:
        print("\n@@@ Customer not found, account creation flow terminated! @@@")
        return

    account = CheckingAccount.new_account(customer=customer, number=account_number)
    accounts.append(account)
    customer.accounts.append(account)

    print("\n=== Account created successfully! ===")


def list_accounts(accounts):
    """Lists all existing accounts in the system.

    Args:
        accounts (list): The account list.
    """
    for account in accounts:
        print("=" * 100)
        print(textwrap.dedent(str(account)))


def main():
    """Main function of the banking system."""
    customers = []
    accounts = []

    while True:
        option = menu()

        if option == "1":
            deposit(customers)

        elif option == "2":
            withdraw(customers)

        elif option == "3":
            display_statement(customers)

        elif option == "6":
            create_customer(customers)

        elif option == "4":
            account_number = len(accounts) + 1
            create_account(account_number, customers, accounts)

        elif option == "5":
            list_accounts(accounts)

        elif option == "7":
            break

        else:
            print("\n@@@ Invalid operation, please select the desired operation again. @@@")


if __name__ == "__main__":
    main()
