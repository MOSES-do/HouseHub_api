
#!/usr/bin/python3
"""
Contains the class DBStorage
"""

from v2.extensions import db

classes = {"Registration": Registration, "TokenBlacklist": TokenBlacklist}


class DBStorage:
    """interaacts with the MySQL database"""
    __session = db

    def all(self, cls=None):
        """query on the current database session"""
        new_dict = {}
        for clss in classes:
            if cls is None or cls is classes[clss] or cls is clss:
                objs = self.__session.query(classes[clss]).all()
                for obj in objs:
                    key = obj.__class__.__name__ + '.' + obj.id
                    new_dict[key] = obj
        return (new_dict)

    def new(self, obj):
        """add the object to the current database session"""
        self.__session.add(obj)

    def save(self):
        """commit all changes of the current database session"""
        self.__session.commit()

    """
    def table_names(self):
        metadata = MetaData()
        metadata.reflect(bind=self.__engine)
        cls = []
        table_list = []
        with self.__engine.connect() as connection:
            for table_name, table in metadata.tables.items():
                table_obj = Table(
                    table_name, metadata, autoload_with=self.__engine
                )
                if table_name == "place_amenity":
                    continue
                else:
                    cls.append(table_name)
        cls.sort(key=str.lower)
        return cls
    """

    def delete(self, obj=None):
        """delete from the current database session obj if not None"""
        if obj is not None:
            self.__session.delete(obj)


    def close(self):
        """call remove() method on the private session attribute"""
        self.__session.remove()

    def get(self, cls, id):
        """
        Returns the object based on the class name and its ID, or
        None if not found
        """
        if cls not in classes.values():
            return None

        all_cls = models.storage.all(cls)
        for value in all_cls.values():
            if (value.id == id):
                return value

        return None

    def count(self, cls=None):
        """
        count the number of objects in storage
        """
        all_class = classes.values()

        if not cls:
            count = 0
            for clas in all_class:
                count += len(models.storage.all(clas).values())
        else:
            count = len(models.storage.all(cls).values())

        return count
