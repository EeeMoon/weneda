from weneda import FG
from tests.table import Table


t = Table(4)

t.add_row([FG.BLUE+"111"+FG.DEFAULT, "2s131", "aa\naad"])
t.add_row(["s", "sdfs"])
t.add_row(["ad", None, "12ппппппппппппппппппп31", "gdfd"])


with open('text.txt', 'w+') as f:
    f.write(t.draw())
    
print(t.draw())
