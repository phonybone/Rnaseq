#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *

# usage: 


class TestStep(Command):
    def usage(self):
        "ts <step_class>"

    def description(self):
        "dummy command for testing steps as classes"


    def run(self, *argv, **args):
        try:
            (stepname)=argv[0][2]
            config=args['config']
        except KeyError as ke:
            raise MissingArgError(str(ke))
        except ValueError as ie:
            raise UserError(self.usage())

        print "stepname is %s" % stepname
        step=self.new_step(stepname)
        print "step is %s" % step
        step.fred()

    def new_step(self,stepname):
        dot_path="Rnaseq.steps.%s" % stepname
        mod=__import__(dot_path)
        steps_mod=mod.steps
        step_mod=getattr(steps_mod, stepname)
        klass=getattr(step_mod, stepname.capitalize())
        obj=klass(name=stepname, type='step')
        return obj


#print __file__, "checking in"
