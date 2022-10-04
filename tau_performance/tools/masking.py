import operator
import numpy as np

OPERATORS = {
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '>': operator.gt,
    '<': operator.lt
}


class GeneralCut:
    """ Cuts based on string """
    def __init__(self, cut_string):
        """ Initializes the string based cut class

        Args:
            cut_string : str
                String containing all the cuts in a default convention

        Returns:
            None
        """
        self.cut_string = cut_string
        self._all_cuts = []
        self.separate_cuts()

    def separate_cuts(self):
        """ Separates all the cuts in the general cut string """
        self.cut_string = self.cut_string.replace(" ", "")
        raw_cuts = self.cut_string.split("&&")
        for cut_ in raw_cuts:
            self._all_cuts.append(self.interpret_single_cut_string(cut_))
        return self._all_cuts

    def interpret_single_cut_string(self, cut_string):
        """ Interpretes the single-cut string """
        cut = ''
        for operator in OPERATORS.keys():
            if operator in cut_string:
                cut = cut_string.split(operator)
                cut.insert(1, operator)
                return cut
        if cut == '':
            raise ValueError('No cut selected')

    @property
    def all_cuts(self):
        return self._all_cuts


class Masks:
    def __init__(self, events, mask_type, obj_type, cfg):
        self.events = events
        self.cfg = cfg
        self.mask_type = mask_type
        self.obj_type = obj_type
        self.eff_type = "eff" if obj_type == cfg.genTau else "fake"
        self.denominator = True if mask_type == 'denominators' else False
        self._masks = {}
        self.base_mask = self.create_base_mask()
        self.create_masks()

    def read_mask_type(self, mask_full_info):
        wp_cuts = {}
        for working_point in mask_full_info:
            cut_string = mask_full_info[working_point]
            gc = GeneralCut(cut_string)
            wp_cuts[working_point] = gc.all_cuts
        return wp_cuts

    def create_base_mask(self):
        base_mask_str = self.cfg[f"TauID_{self.eff_type}"][self.mask_type].Base
        gc = GeneralCut(base_mask_str)
        total_mask = np.array([0] * len(self.events))
        for cut_ in gc.all_cuts:
            var_name, abs_value = interpret_name(
                                                cut_[0], self.cfg,
                                                denominator=self.denominator,
                                                obj_type=self.obj_type)
            value = float(cut_[2])
            if abs_value:
                var_values = np.abs(self.events[var_name])
            else:
                var_values = self.events[var_name]
            mask = OPERATORS[cut_[1]](var_values, value).to_numpy()
            total_mask += mask.astype(int)
        base_mask = total_mask == len(gc.all_cuts)
        return base_mask

    def create_masks(self):
        self.read_all_masks()
        for mask_key, mask_values in self._masks.items():
            wp_masks = {}
            for wp_key in mask_values:
                wp_masks[wp_key] = self.create_single_mask(mask_values[wp_key])
            self._masks[mask_key] = wp_masks
        if len(self._masks) == 0:
            self._masks = self.base_mask

    def create_single_mask(self, wp_mask):
        total_mask = np.array([0] * len(self.events))
        for cut in wp_mask:
            value = float(cut[2])
            var_name, abs_value = interpret_name(
                                                cut[0], self.cfg,
                                                denominator=self.denominator,
                                                obj_type=self.obj_type)
            if abs_value:
                var_values = np.abs(self.events[var_name])
            else:
                var_values = self.events[var_name]
            mask = OPERATORS[cut[1]](var_values, value).to_numpy()
            total_mask += mask.astype(int)
        current_mask = total_mask == len(wp_mask)
        wp_mask = current_mask & self.base_mask
        return wp_mask

    def read_all_masks(self):
        for mask in self.cfg[f"TauID_{self.eff_type}"][self.mask_type]:
            if not mask == 'Base':
                self._masks[mask] = self.read_mask_type(
                       self.cfg[f"TauID_{self.eff_type}"][self.mask_type][mask])

    @property
    def masks(self):
        return self._masks


def interpret_name(name, cfg, denominator=False, obj_type=None):
    """ If the name contains the sign '@' then this means this is already the
    full name """
    abs_value = False
    if denominator:
        name = f"{obj_type}_{name}"
    elif '@' not in name:
        name = f"{cfg.comparison_tau}_{name}"
    if '|' in name:
        abs_value = True
        name = name.replace("|", "")
    return name, abs_value
