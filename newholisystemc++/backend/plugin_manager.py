import os
import importlib.util
from PyQt6.QtCore import QObject, pyqtSignal

class PluginManager(QObject):
    plugin_loaded = pyqtSignal(str)
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PluginManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False): return
        super().__init__()
        self._initialized = True
        self.plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")
        self.active_plugins = {}
        
        if not os.path.exists(self.plugins_dir):
            try:
                os.makedirs(self.plugins_dir)
                self._create_example_plugin()
            except Exception as e:
                print(f"Could not create plugins directory: {e}")

    def load_all_plugins(self, main_window=None):
        if not os.path.exists(self.plugins_dir): return
        
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                self.load_plugin(filename, main_window)

    def load_plugin(self, filename, main_window=None):
        name = filename[:-3]
        filepath = os.path.join(self.plugins_dir, filename)
        try:
            spec = importlib.util.spec_from_file_location(name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'setup'):
                # Pass the main window context so the plugin can add tabs, docks, or menu items
                plugin_instance = module.setup(main_window)
                self.active_plugins[name] = plugin_instance
                self.plugin_loaded.emit(name)
                print(f"Loaded plugin: {name}")
        except Exception as e:
            print(f"Failed to load plugin {name}: {e}")

    def _create_example_plugin(self):
        example_path = os.path.join(self.plugins_dir, "example_plugin.py")
        with open(example_path, "w") as f:
            f.write('''"""
Example Plugin for SystemHero
To use, ensure the main dashboard passes itself to `setup`.
"""
from PyQt6.QtWidgets import QMessageBox

def setup(main_window):
    print("Example Plugin initialized!")
    return "ExamplePlugin"
''')
