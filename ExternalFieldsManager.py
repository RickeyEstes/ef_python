import sys

from Vec3d import Vec3d
from ExternalFieldsUniform import ExternalFieldMagneticUniform, ExternalFieldElectricUniform
from ExternalFieldsOnRegularGridFromFile import ExternalFieldMagneticOnRegularGridFromFile


class ExternalFieldsManager():

    def __init__(self):
        self.electric = []
        self.magnetic = []


    @classmethod
    def init_from_config(cls, conf):
        new_obj = cls()
        new_obj.electric = []
        new_obj.magnetic = []
        for sec_name in conf:
            if ExternalFieldMagneticUniform.is_magnetic_uniform_config_part(sec_name):
                new_obj.magnetic.append(
                    ExternalFieldMagneticUniform.init_from_config(conf[sec_name], sec_name))
            elif ExternalFieldElectricUniform.is_electric_uniform_config_part(sec_name):
                new_obj.electric.append(
                    ExternalFieldElectricUniform.init_from_config(conf[sec_name], sec_name))
            elif ExternalFieldMagneticOnRegularGridFromFile.is_relevant_conf_part(sec_name):
                new_obj.magnetic.append(
                    ExternalFieldMagneticOnRegularGridFromFile.init_from_config(
                        conf[sec_name], sec_name))
        return new_obj


    @classmethod
    def init_from_h5(cls, h5_external_fields_group):
        new_obj = cls()
        new_obj.electric = []
        new_obj.magnetic = []
        for field_name in h5_external_fields_group.keys():
            current_field_grpid = h5_external_fields_group[field_name]
            new_obj.parse_hdf5_external_field(current_field_grpid)
        return new_obj

    
    def parse_hdf5_external_field(self, current_field_grpid):
        field_type = current_field_grpid.attrs["field_type"]
        if field_type == "magnetic_uniform":
            self.magnetic.append(
                ExternalFieldMagneticUniform.init_from_h5(current_field_grpid))
        elif field_type == "electric_uniform":
            self.electric.append(
                ExternalFieldElectricUniform.init_from_h5(current_field_grpid))
        elif field_type == "magnetic_on_regular_grid_from_file":
            self.magnetic.append(
                ExternalFieldMagneticOnRegularGridFromFile.init_from_h5(
                    current_field_grpid))
        else:
            print("In External_field_manager constructor-from-h5: ")
            print("Unknown external_field type. Aborting")
            sys.exit(-1)


    def total_electric_field_at_particle_position(self, particle, current_time):
        total_el_field = Vec3d.zero()
        for f in self.electric:
            el_field = f.field_at_particle_position(particle, current_time)
            total_el_field = total_el_field.add(el_field)
        return total_el_field


    def total_magnetic_field_at_particle_position(self, particle, current_time):
        total_mgn_field = Vec3d.zero()
        for f in self.magnetic:
            mgn_field = f.field_at_particle_position(particle, current_time)
            total_mgn_field = total_mgn_field.add(mgn_field)
        return total_mgn_field


    def write_to_file(self, hdf5_file_id):
        hdf5_groupname = "/External_fields"
        n_of_electric_fields = len(self.electric)
        n_of_magnetic_fields = len(self.magnetic)
        fields_group = hdf5_file_id.create_group(hdf5_groupname)
        fields_group.attrs.create("number_of_electric_fields", n_of_electric_fields)
        fields_group.attrs.create("number_of_magnetic_fields", n_of_magnetic_fields)
        for el_field in self.electric:
            el_field.write_to_file(fields_group)
        for mgn_field in self.magnetic:
            mgn_field.write_to_file(fields_group)


    def print_fields(self):
        for el_field in self.electric:
            el_field.print()
        for mgn_field in self.magnetic:
            mgn_field.print()
