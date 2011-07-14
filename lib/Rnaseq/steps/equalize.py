from Rnaseq import *

# fixme: nyi
class equalize(Step):


    def outputs(self):
        return ['${ID}_GOOD_1.${format}', '${ID}_GOOD_2.${format}']
    
