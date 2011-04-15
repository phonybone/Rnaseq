#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *

# usage: 


class Update(Command):
    def usage(self):
        return "usage: update <class> <id> [field=value]+"

    def description(self):
        return "update a database object"

    def run(self, *argv, **args):
        try:
            config=args['config']
            (classname,id,field,value)=argv[0][2:6]

        except ValueError as ie:
            raise UserError(self.usage())

        session=RnaseqGlobals.get_session()

        up_dict={}
        for pair in argv[0][3:]:
            try:
                (field,val)=re.split("=",pair,maxsplit=2)
                up_dict[field]=val
            except ValueError as e:
                pass

        klass=globals()[classname]
        result=session.query(klass).filter_by(id=id).update(up_dict)
        session.commit()



