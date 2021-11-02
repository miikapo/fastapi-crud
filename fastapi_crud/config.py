class CRUDConfig:
    read_one = True
    read_all = True
    create = True
    delete = True

    create_schema_exclude_fields = []
    read_schema_exclude_fields = []


class RelationshipConfig(CRUDConfig):
    read_single = False
    delete = False
