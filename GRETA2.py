import MDAnalysis as mda
from MDAnalysis.analysis import dihedrals, distances
import numpy as np
from MDAnalysis.analysis.dihedrals import Dihedral
from read_input import read_gro_bonds, read_gro_angles, read_gro_dihedrals
import pandas as pd
import itertools
from itertools import product, combinations
from atomtypes_definitions import gromos_atp
from protein_configuration import distance_cutoff, distance_residue

#native_pdb = mda.Universe('GRETA/native/pep.pdb', guess_bonds = True) # Da spostare su read pdb
native_bonds =  read_gro_bonds()
native_angles = read_gro_angles()
native_dihedrals = read_gro_dihedrals()

def make_pdb_atomtypes (native_pdb, fibril_pdb, pep_gro_atoms):

    native_sel = native_pdb.select_atoms('all')
    native_atomtypes = []
    ffnb_sb_type = []
    ffnb_residue = []
    ffnb_name = []
    for atom in native_sel:
        # Also the chain ID is printed along because it might happen an interaction between two atoms of different 
        # chains but of the same residue which would be deleted based only by the eclusion list as example
        # CA_1 N_1 is in the exclusion list but in fibril might interact the CA_1 chain 1 with N_1 chain 2
        atp = str(atom.name) + '_' + str(atom.resnum) + ':' + str(atom.segid)
        native_atomtypes.append(atp)

        # This part is for attaching to FFnonbonded.itp
        sb_type = str(atom.name) + '_' + str(atom.resnum)
        ffnb_sb_type.append(sb_type)
        res_ffnb = str(atom.resname)
        ffnb_residue.append(res_ffnb)
        name = str(atom.name)
        ffnb_name.append(name) # Questo per quando verranno definiti meglio 
                               # gli atomtypes

    
    fibril_sel = fibril_pdb.select_atoms('all')
    fibril_atomtypes = []
    for atom in fibril_sel:
        atp = str(atom.name) + '_' + str(atom.resnum) + ':' + str(atom.segid)
        fibril_atomtypes.append(atp)
    

    # ffnonbonded making
    # Making a dictionary with atom number and type

    ffnb_atomtype = pd.DataFrame(columns = ['; type', 'name', 'chem', 'residue', 'at.num', 'mass', 'charge', 'ptype', 'c6', 'c12'])

    ffnb_atomtype['; type'] = ffnb_sb_type
    ffnb_atomtype['name'] = ffnb_name
    ffnb_atomtype['chem'] = pep_gro_atoms['type']
    ffnb_atomtype['residue'] = ffnb_residue
    ffnb_atomtype['at.num'] = ffnb_atomtype['chem'].map(gromos_atp['at.num'])
    #ffnb_atomtype['mass'] = pep_gro_atoms['mass']
    ffnb_atomtype['mass'] = ffnb_atomtype['chem'].map(gromos_atp['mass'])
    ffnb_atomtype['charge'] = '0.000000'
    ffnb_atomtype['ptype'] = 'A'
    ffnb_atomtype['c6'] = '0.00000e+00'
    ffnb_atomtype['c12'] = ffnb_atomtype['chem'].map(gromos_atp['c12'])
    ffnb_atomtype['c12'] = ffnb_atomtype["c12"].map(lambda x:'{:.6e}'.format(x))
    ffnb_atomtype.drop(columns = ['chem', 'residue', 'name'], inplace = True)
    
    atomtypes_atp = ffnb_atomtype[['; type', 'mass']].copy()

    return native_atomtypes, fibril_atomtypes, ffnb_atomtype, atomtypes_atp

def make_exclusion_list (structure_pdb, native_bonds, native_angles, native_dihedrals, native_impropers):
    
    exclusion_list = []
    for index, row in native_bonds.iterrows():
        # For every bonds two atoms are defined and for every atom it is retrieved the atomtype
        exclusion_list.append(str(structure_pdb.atoms[row['ai'] - 1].name) + '_' + str(structure_pdb.atoms[row['ai'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['aj'] - 1].name) + '_' + str(structure_pdb.atoms[row['aj'] - 1].resnum))   
    
    print('Exclusion List from bonds:               ', len(exclusion_list)) # 87

    for index, row in native_angles.iterrows():
        exclusion_list.append(str(structure_pdb.atoms[row['ai'] - 1].name) + '_' + str(structure_pdb.atoms[row['ai'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['aj'] - 1].name) + '_' + str(structure_pdb.atoms[row['aj'] - 1].resnum))
        exclusion_list.append(str(structure_pdb.atoms[row['ai'] - 1].name) + '_' + str(structure_pdb.atoms[row['ai'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['ak'] - 1].name) + '_' + str(structure_pdb.atoms[row['ak'] - 1].resnum))
        exclusion_list.append(str(structure_pdb.atoms[row['aj'] - 1].name) + '_' + str(structure_pdb.atoms[row['aj'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['ak'] - 1].name) + '_' + str(structure_pdb.atoms[row['ak'] - 1].resnum))
    
    print('Addition of angles to exclusion list:    ', len(exclusion_list)) # 447


    for index, row in native_dihedrals.iterrows():
        exclusion_list.append(str(structure_pdb.atoms[row['ai'] - 1].name) + '_' + str(structure_pdb.atoms[row['ai'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['aj'] - 1].name) + '_' + str(structure_pdb.atoms[row['aj'] - 1].resnum))
        exclusion_list.append(str(structure_pdb.atoms[row['ai'] - 1].name) + '_' + str(structure_pdb.atoms[row['ai'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['ak'] - 1].name) + '_' + str(structure_pdb.atoms[row['ak'] - 1].resnum))
        exclusion_list.append(str(structure_pdb.atoms[row['ai'] - 1].name) + '_' + str(structure_pdb.atoms[row['ai'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['al'] - 1].name) + '_' + str(structure_pdb.atoms[row['al'] - 1].resnum))
        exclusion_list.append(str(structure_pdb.atoms[row['aj'] - 1].name) + '_' + str(structure_pdb.atoms[row['aj'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['ak'] - 1].name) + '_' + str(structure_pdb.atoms[row['ak'] - 1].resnum))
        exclusion_list.append(str(structure_pdb.atoms[row['aj'] - 1].name) + '_' + str(structure_pdb.atoms[row['aj'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['al'] - 1].name) + '_' + str(structure_pdb.atoms[row['al'] - 1].resnum))
        exclusion_list.append(str(structure_pdb.atoms[row['ak'] - 1].name) + '_' + str(structure_pdb.atoms[row['ak'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['al'] - 1].name) + '_' + str(structure_pdb.atoms[row['al'] - 1].resnum))

    print('Addition of dihedrals to exclusion list: ', len(exclusion_list)) # 861

    for index, row in native_impropers.iterrows():
        exclusion_list.append(str(structure_pdb.atoms[row['ai'] - 1].name) + '_' + str(structure_pdb.atoms[row['ai'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['aj'] - 1].name) + '_' + str(structure_pdb.atoms[row['aj'] - 1].resnum))
        exclusion_list.append(str(structure_pdb.atoms[row['ai'] - 1].name) + '_' + str(structure_pdb.atoms[row['ai'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['ak'] - 1].name) + '_' + str(structure_pdb.atoms[row['ak'] - 1].resnum))
        exclusion_list.append(str(structure_pdb.atoms[row['ai'] - 1].name) + '_' + str(structure_pdb.atoms[row['ai'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['al'] - 1].name) + '_' + str(structure_pdb.atoms[row['al'] - 1].resnum))
        exclusion_list.append(str(structure_pdb.atoms[row['aj'] - 1].name) + '_' + str(structure_pdb.atoms[row['aj'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['ak'] - 1].name) + '_' + str(structure_pdb.atoms[row['ak'] - 1].resnum))
        exclusion_list.append(str(structure_pdb.atoms[row['aj'] - 1].name) + '_' + str(structure_pdb.atoms[row['aj'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['al'] - 1].name) + '_' + str(structure_pdb.atoms[row['al'] - 1].resnum))
        exclusion_list.append(str(structure_pdb.atoms[row['ak'] - 1].name) + '_' + str(structure_pdb.atoms[row['ak'] - 1].resnum) + '_' + str(structure_pdb.atoms[row['al'] - 1].name) + '_' + str(structure_pdb.atoms[row['al'] - 1].resnum))
    
    print('Addition of impropers to exclusion list: ', len(exclusion_list)) # 1119

    # Keep only unique values
    exclusion_list = list(set(exclusion_list))
    print('Drop duplicates in the exclusion list:   ', len(exclusion_list)) # 350
    return exclusion_list


################################ PAIRS

def make_pairs (structure_pdb, exclusion_list, atomtype):

    print('\n\t Measuring distances between all atom in the pdb')
    # Selection of all the atoms required to compute LJ
    atom_sel = structure_pdb.select_atoms('all')
    # Calculating all the distances between atoms
    # The output is a combination array 
    self_distances = distances.self_distance_array(atom_sel.positions)
    print('\t Number of distances measured :', len(self_distances))

    print('\n\t Preparing the atomtype array')
    
    # Making a list of the atomtypes of the protein
    # Da spostare su atomtypes_definitions
    #atomtype = []
    #for atom in atom_sel:
    #    # Also the chain ID is printed along because it might happen an interaction between two atoms of different 
    #    # chains but of the same residue which would be deleted based only by the eclusion list as example
    #    # CA_1 N_1 is in the exclusion list but in fibril might interact the CA_1 chain 1 with N_1 chain 2
    #    atp = str(atom.name) + '_' + str(atom.resnum) + ':' + str(atom.segid)
    #    atomtype.append(atp)

    # Combining all the atomtypes in the list to create a pair list corresponding to the distance array
    pairs_list = list(itertools.combinations(atomtype, 2))
    pairs_ai = []
    pairs_aj = []
    # But the combinations are list of list and we need to separate them
    for n in range(0, len(pairs_list)):
        i = pairs_list[n][0]
        pairs_ai.append(i)
        j = pairs_list[n][1]
        pairs_aj.append(j)
    print('\t Atomtype array ready')

    print('\n\t Creating the pairs dataframes')
    # Creation of the dataframe containing the ffnonbonded.itp
    structural_LJ = pd.DataFrame(columns = ['ai', 'aj', 'distance', 'sigma', 'epsilon', 'check'])
    structural_LJ['ai'] = pairs_ai
    structural_LJ['aj'] = pairs_aj
    structural_LJ['distance'] = self_distances
    print('\t Raw pairs list ', len(structural_LJ))
    
    print('\n\t Extracting chain label for every atom pair')
    structural_LJ[['ai', 'chain_ai']] = structural_LJ.ai.str.split(":", expand = True)
    structural_LJ[['aj', 'chain_aj']] = structural_LJ.aj.str.split(":", expand = True)

    # Create the check column for the exclusion list
    structural_LJ['check'] = structural_LJ['ai'] + '_' + structural_LJ['aj']
    same_chain = np.where(structural_LJ['chain_ai'] == structural_LJ['chain_aj'], 'Yes', 'No')
    structural_LJ['same_chain'] = same_chain
    
    print('\t Tagging the chain association')
    are_same = structural_LJ.loc[structural_LJ['same_chain'] == 'Yes']
    not_same = structural_LJ.loc[structural_LJ['same_chain'] == 'No']
    
    print('\t Pairs within the same chain: ', len(are_same))
    print('\t Pairs not in the same chain: ', len(not_same))
    print('\t Raw pairs list ', len(structural_LJ))

    print('\t Tagging pairs included in bonded exclusion list')
    # Here we keep only the one without the exclusions
    structural_LJ['exclude'] = ''
    structural_LJ.loc[(structural_LJ['check'].isin(exclusion_list)), 'exclude'] = 'Yes'

    to_exclude = structural_LJ.loc[structural_LJ['exclude'] == 'Yes']
    print('\t All pairs present in the bonded exclusion list: ', len(to_exclude))

    mask = (structural_LJ.exclude == 'Yes') & (structural_LJ.same_chain == 'Yes')
    structural_LJ = structural_LJ[~mask]
    print('\t Pairs in the same chain and included in the exclusion list :', len(mask))
    print('\t After exclusion list and chain selection', len(structural_LJ))

    print('\n\t Applying distance cutoff of 6A')
    # Keep only the atoms within 6 A
    structural_LJ = structural_LJ[structural_LJ.distance < distance_cutoff] # PROTEIN CONFIGURATION
    print('\t Pairs below cutoff 6: ', len(structural_LJ))

    print('\t Applying residue number cutoff of 3')
    # This part is to filter more the LJ like in smog: if two pairs are made by aminoacids closer than
    # 3 they'll be deleted. Therefore aminoacids 1, 2, 3 and 4 does not make any contacts.
    # Therefore I copy the LJ dataframe and apply some more filters
    structural_LJ[['type_ai', 'resnum_ai']] = structural_LJ.ai.str.split("_", expand = True)
    structural_LJ[['type_aj', 'resnum_aj']] = structural_LJ.aj.str.split("_", expand = True)
    # And to do that it is necessary to convert the two columns into integer
    structural_LJ = structural_LJ.astype({"resnum_ai": int, "resnum_aj": int})
    structural_LJ['diff'] = ''
    
    
    # Da riattivare successivamente, test tenendo solo exlcusion list bonded e non SB
    structural_LJ.drop(structural_LJ[(abs(structural_LJ['resnum_aj'] - structural_LJ['resnum_ai']) < distance_residue) & (structural_LJ['same_chain'] == 'Yes')].index, inplace = True)    
    
    structural_LJ['diff'] = abs(structural_LJ['resnum_aj'] - structural_LJ['resnum_ai'])
    print('\t All the pairs further than 3 aminoacids and not in the same chain: ', len(structural_LJ))

    print('\n\t Making the reverse duplicate dataframe')
    # Inverse pairs calvario
    inv_LJ = structural_LJ[['aj', 'ai', 'distance', 'sigma', 'epsilon', 'check', 'chain_ai', 'chain_aj', 'same_chain', 'exclude', 'type_ai', 'resnum_ai', 'type_aj', 'resnum_aj', 'diff']].copy()
    inv_LJ.columns = ['ai', 'aj', 'distance', 'sigma', 'epsilon', 'check', 'chain_ai', 'chain_aj', 'same_chain', 'exclude', 'type_ai', 'resnum_ai', 'type_aj', 'resnum_aj', 'diff']
    structural_LJ = structural_LJ.append(inv_LJ, sort = False, ignore_index = True)
    print('\t Doubled pairs list: ', len(structural_LJ))

    print('\t Sorting and dropping all the duplicates')
    # Sorting the pairs
    structural_LJ.sort_values(by = ['ai', 'aj', 'distance'], inplace = True)
    # Cleaning the duplicates
    structural_LJ = structural_LJ.drop_duplicates(subset = ['ai', 'aj'], keep = 'first')
    # Removing the reverse duplicates
    cols = ['ai', 'aj']
    structural_LJ[cols] = np.sort(structural_LJ[cols].values, axis=1)
    structural_LJ = structural_LJ.drop_duplicates()
    print('\t Cleaning Complete ', len(structural_LJ))
    print('\n\t Calculating sigma and epsilon')
    
    structural_LJ['sigma'] = (structural_LJ['distance']/10) / (2**(1/6))
    structural_LJ['sigma'] = structural_LJ["sigma"].map(lambda x:'{:.6e}'.format(x))

    structural_LJ['epsilon'] = 2.49 # PROTEIN CONFIGURATION

    print('\n\n\t Sigma and epsilon completed ', len(structural_LJ))
    


    return structural_LJ

def merge_GRETA(native_pdb_pairs, fibril_pdb_pairs):
    # Merging native and fibril LJ pairs and cleaning all the duplicates among them
    greta_LJ = native_pdb_pairs.append(fibril_pdb_pairs, sort = False, ignore_index = True)

    # Sorting the pairs
    greta_LJ.sort_values(by = ['ai', 'aj', 'distance'], inplace = True)
    # Cleaning the duplicates
    greta_LJ = greta_LJ.drop_duplicates(subset = ['ai', 'aj'], keep = 'first')
    # Removing the reverse duplicates
    cols = ['ai', 'aj']
    greta_LJ[cols] = np.sort(greta_LJ[cols].values, axis=1)
    greta_LJ = greta_LJ.drop_duplicates()



    #check_GRETA = greta_LJ[['ai', 'aj']].copy()

    # Drop columns
    greta_LJ.insert(2, 'type', 1)
    greta_LJ.drop(columns = ['distance', 'check', 'chain_ai', 'chain_aj', 'same_chain', 'exclude', 'type_ai', 'resnum_ai', 'type_aj', 'resnum_aj', 'diff'], inplace = True)
    greta_LJ = greta_LJ.rename(columns = {'ai':'; ai'})

    return greta_LJ#, check_GRETA


    
########################## DIHEDRALS

def sb_dihedrals (structure_pdb):
    phi_dihedrals = []
    for index, row in native_dihedrals.iterrows():
        # Here are selected only the atom numbers for every dihedral from the pdb structure
        # ANCORA DA FINIRE PERCHE' I DIEDRI DA PDB NON STANNO CORRISPONDENDO
        atom_selection = structure_pdb.atoms[row['ai'] - 1] + structure_pdb.atoms[row['aj'] - 1] + structure_pdb.atoms[row['ak'] - 1] + structure_pdb.atoms[row['al'] - 1]
        phi = atom_selection.dihedral.value()
        phi_dihedrals.append(phi)

    native_dihedrals['func'] = 9
    native_dihedrals['phi'] = phi_dihedrals
    native_dihedrals['kd'] = ''
    native_dihedrals['mult'] = ''  # manca questa
    #print(native_dihedrals)
    return native_dihedrals