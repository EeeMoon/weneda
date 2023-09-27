from weneda import FG
from tests.table import Table


t = Table()

t.add_row([FG.RED + "111", "2s131", "aa\naad"])
t.add_row([FG.RED+ "s", "sdfs"])
t.add_row([FG.RED +"ad", None, "12ппппппппппппппппппп31", "gdfd"])


print(t.draw())