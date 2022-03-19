import os


def exec_cmd(cmd: str) -> str:
    stream = os.popen(cmd)
    return stream.read()


def calculate_acceptance_modhash():
    return exec_cmd('cdv clsp treehash -i drivers/include drivers/acceptance.clsp').strip('\n')


def calculate_initiation_curry_treehash(acceptance_modhash: str,
                                        player1_puzzlehash: str,
                                        player1_hashed_preimage: str,
                                        amount: str):
    clsp = exec_cmd(
        f"cdv clsp curry -i drivers/include drivers/initiation.clsp -a 0x{acceptance_modhash} -a 0x{player1_puzzlehash} -a 0x{player1_hashed_preimage} -a {amount}")
    return exec_cmd(f"opc -H '{clsp}'").split('\n')[0]


def calculate_initiation_soln_treehash(acceptance_modhash: str,
                                       player1_puzzlehash: str,
                                       player1_hashed_preimage: str,
                                       amount: str,
                                       player2_puzzlehash: str,
                                       player2_preimage: str):
    init_puzzle = exec_cmd(
        f"cdv clsp curry -i drivers/include drivers/initiation.clsp -a 0x{acceptance_modhash} -a 0x{player1_puzzlehash} -a 0x{player1_hashed_preimage} -a {amount}")
    init_soln = exec_cmd(f"run '(list {player2_puzzlehash} {player2_preimage})'")
    return exec_cmd(f"brun '{init_puzzle}' '{init_soln}'").strip('\n').strip('(').strip(')').strip("0x").split(' ')[1]


def expected_acceptance_puzzlehash(
        player1_puzzlehash: str,
        player1_hashed_preimage: str,
        amount: str,
        player2_puzzlehash: str,
        player2_preimage: str):
    clsp = exec_cmd(
        f"cdv clsp curry -i drivers/include drivers/acceptance.clsp -a 0x{player1_puzzlehash} -a 0x{player1_hashed_preimage} -a {amount} -a 0x{player2_puzzlehash} -a 0x{player2_preimage}")
    return exec_cmd(f"opc -H '{clsp}'").split('\n')[0]
