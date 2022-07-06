'A simple database module that made by module shelve.'
import sys, shelve

__author__='qfcy'
__email__='3416445406@qq.com'
__version__='1.0.1'
_TITLE="database"

class DataBase(shelve.DbfilenameShelf):
    """A database that can undo.It has inherited from the DbfilenameShelf object
in module shelve."""
    def __init__(self, filename, flag='c', protocol=None, writeback=False):
        super().__init__(filename, flag, protocol, writeback)
        self.prev=[]
    def __setitem__(self,key,value):
        self.prev.append(self.copy())
        super().__setitem__(key,value)
    def clear(self):
        self.prev=[]
        super.clear()
    def copy(self):
        new={}
        for key in self:
            new[key]=self[key]
        return new
    def undo(self):
        if self.prev:
            last=self.prev.pop()
            for key in self:
                if key not in last:del self[key]
                else:super().__setitem__(key,last[key])
            print("Undid to the last editing.")
        else:print("Nothing to undo.",file=sys.stderr)
        
        
def store_person(db):
    """
    Query user for data and store it in the shelf object
    """
    try:
        pid = input('Enter unique ID number: ')
        try:person = db[pid]
        except:person={"name":"","age":"","phone":""}
        person['name'] = input('Enter name: ') or person['name']
        person['age'] = input('Enter age: ') or person['age']
        person['phone'] = input('Enter phone number: ') or person['phone']
        db[pid] = person
    except KeyboardInterrupt:
        print("Interrupted by user.",file=sys.stderr)

def lookup_person(db,pid=None):
    """
    Query user for ID and desired field, and fetch the corresponding data from
    the shelf object
    """
    if not pid:pid = input('Enter ID number: ')
    try:print(pid + ':', db[pid])
    except KeyError:print("Error: No information about person {}."\
                          .format(pid),file=sys.stderr)
def print_all_datas(db):
    "Print all the datas from the shelf object"
    if db:
        print("All the informations here:")
        for person in db:
            print("    {}:{}".format(person,db[person]))
    else:
        print("Error: No datas. Your database is empty."
              ,file=sys.stderr)
def remove_person(db):
    pid=input('Enter ID Number: ')
    if pid:del db[pid]
    print("ID %r has removed successfully."% pid)

def clear_data(db):
    result=input("Clear all the informations? ")
    if result.lower().startswith('y'):
        db.clear()
        print("Data has cleared successfully.")

def ask_for_exit(console=None):
    msg="\n^C确实要退出吗?(Y/N) "
    if console:console.ctext(msg,"green",None,"bold",end='')
    else:print(msg,end='')
    try:
        if input().lower().startswith('y'):return 0
    except KeyboardInterrupt:
        return ask_for_exit(console)

def enter_command(console=None):
    inputfunc=getattr(console,"input",input)
    cmd = inputfunc('Enter command (? for help): ')
    return cmd.strip().lower()

def main():
    filename=sys.argv[1] if len(sys.argv)>1 else 'database.dat'
    try:
        import console_tool
        c=console_tool.Console()
        c.colorize()
        c.title("%s - %s" %(_TITLE,filename))
    except ImportError:c=None
    if filename.endswith(".dat"):filename=filename[:-4]
    database = DataBase(filename) # You may want to change this name
    while True:
        try:
            try:
                cmd = enter_command(c)
            except EOFError:#User entered Ctrl+Z
                cmd="undo"                
            if cmd:
                if cmd == 'store':
                    store_person(database)
                elif cmd == 'lookup':
                    lookup_person(database)
                elif cmd=='all':
                    print_all_datas(database)
                elif cmd=='undo':
                    database.undo()
                elif cmd=='remove':
                    remove_person(database)
                elif cmd=='clear':
                    clear_data(database)
                elif cmd == '?' or cmd=='help':
                    print('''The available commands are:
store  : Stores information about a person
lookup : Looks up a person from ID number
all    : Prints informations about everyone
undo (or use Ctrl+Z):Undoes the last editing
remove : Removes a person from ID number
clear  : Clears all the datas
quit (or exit): Save changes and exit
?   (or help): Prints this message''')
                elif cmd == 'quit' or cmd=='exit':
                    return 0
                elif cmd.isdecimal():
                    lookup_person(database,cmd)
                else:
                    print('%r is not an availble command.Enter "?" for help.'\
                          % cmd, file=sys.stderr)
        except (KeyboardInterrupt,SystemExit) as err:
            if type(err)==KeyboardInterrupt:
                if ask_for_exit(c)==0:return 0

if __name__ == '__main__': sys.exit(main())
