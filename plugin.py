import threading
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
   
def add_plugins():
    print("adding plugins")
    def exec_plugin(name):
        if name == "__init__.py":
            return
        name = name.strip(".py")
        __import__("plugins." + name)
        print(f"Loaded plugin {name}!")

    if not os.path.exists(dir_path + "/plugins"):
        os.mkdir(dir_path + "/plugins")
    for plugin in os.listdir(dir_path + "/plugins"):
        if os.path.isdir(dir_path + "/plugins/" + plugin):
            continue
        print(f"Loading plugin {plugin}")
        f = open(dir_path + "/plugins/" + plugin, "r")
        threading.Thread(target=exec_plugin, args=[plugin]).start()