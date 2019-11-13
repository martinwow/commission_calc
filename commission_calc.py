# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 21:22:40 2019

@author: Martin Vavpotič
"""
from datetime import datetime as dt

class Benefit:
    """Defines a benefit of a policy; one policy can have multiple benefits, but only one can be the main benefit,
    others are riders.
    One policy can contain benefits with different start dates, different agencies/agents, different insured persons.
    Duration of benefit is determined by maximum specified duration (per risk) and age of insured person."""
    #Should I include risk code in the benefit? Possibly more than one per benefit!
    
    def __init__(self, report_per, benefit_start_date, benefit_maturity_date, benefit_term, benefit_code, _
                 coverage_prem, insured_person, insured_p_birth_date, agency, agent, main_or_rider):
        #self.policy_number = policy_number
        #self.product = product
        self.report_per = report_per
        self.benefit_start_date = benefit_start_date # String or date? Need to handle all possible formats of date.
        self.benefit_maturity_date = benefit_maturity_date
        self.benefit_term = benefit_term
        self.benefit_code = benefit_code
        self.coverage_prem = coverage_prem
        self.insurer = insurer # Need just an ID, not actual names; might have to connect with identity database
        self.insured_person = insured_person # Can just use insured_person_id; no specifications to the format.
        self.insured_p_birth_date = insured_p_birth_date
        self.agency = agency
        self.agent = agent
        self.main_or_rider = main_or_rider
        # Only when policy is defined can I declare if benefit is main or a rider. Default value should be rider;
        # define extra if main benefit.
        
    # Should include a method that handles all possible formats for date. One option is to use string.
    # How to handle anti-dating?
    
    def age_at_beginning(self):
        start_d = self.benefit_start_date.date()
        birth_d = self.insured_p_birth_date.date()
        
        dur = round( (start_d.year - birth_d.year)
                    +(start_d.month - birth_d.month)
                    /12
                     ,2)
        return dur

    
    def duration_of_benefit(self):
        start_d = self.benefit_start_date.date()
        current_d = self.report_per.date()
        
        dur = round( (current_d.year - start_d.year)
                    +(current_d.month - start_d.month)
                    /12
                     ,2)
        return dur
    
    def agency_info(self,agency_catalogue):
        pass
    # Info about the agency; number is enough so far, might have to access lists to get the full name
        
    def agent_info(self,agent_catalogue):
        pass
    # Info about agents under specific agencies; can one agent be in multiple agencies?
    # How to handle None (no specified agent?)

    
class Policy:
    """Defines a policy which includes one or more benefits. Only one benefit is the main benefit,
    the rest are riders (default value on each benefit).
    Define insurer on policy, not on benefit. Can have multiple insured persons, only one insurer.
    Define policy start date, by designating main benefit we get policy maturity date.
    Define policy cancel date, which is by default None value; if not None value, then trigger storno_procedure
    in Commission class."""
    
    # Initial idea: input should be a flexible number of benefit objects; decided to read from a pandas dataFrame instead.
    # Will call Benefit class while forming the Policy object and put it into a list of Benefit objects.
    #def __init__(self, insurer, policy_start_date, *benefits):
    
    def __init__(self, portfolio): # portfolio is a pandas dataFrame
        self.policy_number = portfelj.loc[0,'POLICY_NUMBER'] # Read from the first line? Possible exceptions?
        self.insurer = portfelj.loc[0,'OWN_TAX_NUMBER']
        self.product = portfelj.loc[0,'PRODUCT_NAME']
        self.payment_freq = portfelj.loc[0,'PAYMENT_FREQ']
        # Possible for benefits of single policy to have different payment frequencies? Probably not,
        # use logging to catch exceptions.
        self.policy_start_date = portfelj.loc[0,'POLICY_START_DATE']
        self.policy_premium = 0 # Base for a sumation of premium over benefits; need a method to do this.
        self.agency = "" #  Agency on Policy? Each benefit has its own, policy agency might be the main benefit's agency.
        self.payment_type = portfelj.loc[0,'RV_MEANING'] # Can have bonus/malus for differet payment types.
        self.benefits = list() # List of objects, instantiated with Benefit class; can be one or more (possible upper limit?)
        self.main_benefit = "" # Filled later by method.
        self.insured_p_age = 0 # Filled later by method.
        self.main_benefit_duration = 0 # Filled later by method.
        

        # benefits is now a list of objects
        for index, line in portfolio.iterrows():
        # Declare benefits in turn as objects, belongs to Policy object
            new_benefit = Benefit(report_per =line['REPORT_PER'], \
                                  benefit_code =line['BENEFIT'], \
                                  benefit_start_date =line['BENEFIT_START_DATE'], \
                                  benefit_maturity_date =line['BENEFIT_MATURITY_DATE'], \
                                  benefit_term =line['BENEFIT_TERM'], \
                                  coverage_prem =line['COVERAGE_PREM'], \
                                  insured_person =line['INSURED_PERSON_ID'], \
                                  insured_p_birth_date =line['INS1_BIRTH_DATE'], \
                                  agency =line['AGENCY'], \
                                  agent =line['AGENT'], \
                                  main_or_rider =line['MAIN_OR_RIDER'])
            if new_benefit.main_or_rider == 1:
                self.agency = new_benefit.agency # Save main benefit's agency to Policy.
                self.main_benefit = new_benefit.benefit_code
                self.insured_p_age = new_benefit.age_at_beginning()
                self.main_benefit_duration = new_benefit.duration_of_benefit()
                        
            #Store new benefit into benefits list.
            self.benefits.append(new_benefit) 
            #Add benefit premium to policy premium
            self.policy_premium += new_benefit.coverage_prem
        
        #Round policy premium to two decimals in case of problems with the floating point; only after all have been added up.
        self.policy_premium = round(self.policy_premium ,2)


class Commission_calc:
    """Commissions_calc class includes all methods needed to calculate the regular and portfolio commission.
    Instead of inheriting  fromthe Policy class, it takes data from the policy object and writes methods to it
    which can later be executed when the proper criteria are fulfilled."""
    
    def __init__(self, policy, catalogue):
        self.policy_number = policy.policy_number
        self.insurer = policy.insurer
        self.product = policy.product
        self.payment_freq = policy.payment_freq
        self.policy_start_date = policy.policy_start_date
        self.policy_premium = policy.policy_premium
        self.agency = policy.agency
        self.tip_placila = policy.tip_placila
        self.main_benefit = policy.main_benefit
        self.insured_p_age = policy.insured_p_age
        self.main_benefit_duration = policy.main_benefit_duration
        #self.portfolio_comm = 0
        self.benefits = policy.benefits
        self.catalogue = catalogue # Catalogue is in JSON format; include it as class attribute? How to update it?

    def catalogue_reduction(catalogue, condition):
        """Generates a shorter dict instead of the original to reduce search time."""
        # WIP
        pass
        
    
    def add_portfolio_commission(self):
        """ Reduce the catalogue first, use commission type, agency, product and in case of ZZ04 benefit. """
        
        new_catalogue = catalogue_reduction(self.catalogue, 'P')
        new_catalogue = catalogue_reduction(new_catalogue, self.agency)
        new_catalogue = catalogue_reduction(new_catalogue, self.product)
        #new_catalogue = catalogue_reduction(new_catalogue, self.main_benefit)
        
         
        # If date_end is unspecified, this is an active time period interval, should be used for new policies.
        for each_key in new_catalogue:
            if new_catalogue[each_key]['date_end'] == None:
                
            else
            
            if each_key[-1] == 1:
                pass 
            elif new_catalogue[each_key]['date_end'] == None:
                pass 
                
        self.portfolio_comm = self.product_choice('ZZ04', new_catalogue) #, self.main_benefit, self.insured_p_age, self.main_benefit_duration, self.policy_premium)#, \
                #portfolio_commission_zz04, portf_provizija)
        #    else:
        #        pass # No product found; logging error that user should check if catalogue is incomplete.

    
    def product_choice(self, product, catalogue):#, product, benefit, obračun):#, method_1, method_2):
        #nov_catalogue = catalogue_reduction(catalogue, product)
        
        if self.product == product:
            new_catalogue = catalogue_reduction(catalogue, self.main_benefit)
            commission = self.portfolio_commission_zz04(new_catalogue)#, self.main_benefit, self.person_age, self.policy_duration, self.premium)
        else:
            commission = self.portf_provizija(self.catalogue[each_key]['procent'])
        return commission

    def portfolio_commission_zz04(self, each_key):#, self.benefit, self.age, self.duration, self.premium):
        commission = 1
        if self.main_benefit in each_key:
            commission = self.age_division(self.catalogue[each_key]['procent'])#, age, duration, premium)
        else:
            commission = each_key # Logging: missing benefit code in the catalogue; possible error.
        return commission
    
    def age_division(self, key_value):#person_age, duration, premium, 
        # Could have a more generalized shape but only one product has this type of structure so far.
        #commission = 0
        if self.insured_p_age < 40:
            commission = self.duration_division(54, key_value[40][0], key_value[40][1])
        elif self.insured_p_age < 50:
            commission = self.duration_division(54, key_value[50][0], key_value[50][1])
        elif self.insured_p_age < 60:
            commission = self.duration_division(54, key_value[60][0], key_value[60][1])
        else:
            commission = self.duration_division(54, key_value[66][0], key_value[66][1])
        return commission

    def duration_division(self, limit, percent1, percent2):
        #commission = 0
        if self.main_benefit_duration < limit:
            commission = self.portfolio_commission(percent1) #calc_method
        elif self.main_benefit_duration >= limit:
            commission = self.portfolio_commission(percent2) #calc_method
        else:
            pass #Give out error warning? What other possibility?
        return commission  

    def portfolio_commission(self, percent):
        return round(self.policy_premium *percent /100 ,2)

    def add_basic_commission(self):
        """ Add basic commission to benefits inside the policy.
        Calls a sequence of methods, each checks its own crtierion.
        Reduces the initial catalogue of rules to have a minimum number to compare."""
        
        #Limits catalogues to type of commissions = 'R'
        new_catalogue = { each_key: self.catalogue[each_key] for each_key in self.catalogue if 'R' in each_key}
        for each_key in new_catalogue:
            if self.product in each_key:
                self.sort_by_product(each_key)
            else:
                pass #Logging: catalogue does not contain the specified product.
    
    def sort_by_product(self, each_key):
        """ Checks if the product of policy is ZZ04."""
        
        if self.product == 'ZZ04':
            self.check_benefit_in_key(each_key)
        else:
            self.compute_sklep_prov(each_key)

    def check_benefit_in_key(self, each_key):
        """ Checks the main benefit in policy for presence in catalogue. """
        if self.main_benefit in each_key:
            self.compute_sklep_prov(each_key)
        else:
            pass #Logging: exception?
            
    def compute_regular_comm(self, each_key):
        """Actual calculation of regular commission.
        Takes individual benefits from the list, finds the right methods, calculates, returns value."""

        for benefit in self.benefits:
            benefit.obračunana_provizija = comm_type_list[self.catalogue[each_key]['base']](self.catalogue, each_key, benefit)

    def comm_tzp(catalogue, each_key, benefit):
        return round(benefit.coverage_premium \
                    *benefit.payment_freq \
                    *min(benefit.benefit_term, catalogue[each_key]['max_period']) \
                    *catalogue[key]['procent'] \
                    /100 \
                    ,2)

    def comm_N_prem(catalogue, each_key, benefit):
        return round(benefit.coverage_prem \
                    *catalogue[key]['N'] \
                    ,2)

    def comm_fixed(catalogue, each_key, benefit):
        return round(catalogue[each_key]['amount'] \
                    ,2)

    comm_type_list = {'tzp':comm_tzp,'N_prem':comm_N_prem,'fixed':comm_fixed}