from dynaconf import LazySettings

settings = LazySettings(envvar_prefix=False, load_dotenv=True)
