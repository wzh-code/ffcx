# -*- coding: utf-8 -*-
# Copyright (C) 2011 Martin Sandve Alnes
#
# This file is part of FFC (https://www.fenicsproject.org)
#
# SPDX-License-Identifier:    LGPL-3.0-or-later


class UFCFormNames:

    "Encapsulation of the names related to a generated UFC form."

    def __init__(self, name, coefficient_names, ufc_form_classname,
                 ufc_finite_element_classnames, ufc_dofmap_classnames,
                 ufc_coordinate_mapping_classnames):
        """Arguments:

        @param name:
            Name of form (e.g. 'a', 'L', 'M').
        @param coefficient_names:
            List of names of form coefficients (e.g. 'f', 'g').
        @param ufc_form_classname:
            Name of ufc::form subclass.
        @param ufc_finite_element_classnames:
            List of names of ufc::finite_element subclasses (length
            rank + num_coefficients).
        @param ufc_dofmap_classnames:
            List of names of ufc::dofmap subclasses (length rank +
            num_coefficients).
        @param ufc_coordinate_mapping_classnames:
            List of names of ufc::coordinate_mapping subclasses
        """
        assert len(coefficient_names) <= len(ufc_dofmap_classnames)
        assert len(ufc_finite_element_classnames) == len(ufc_dofmap_classnames)

        self.num_coefficients = len(coefficient_names)
        self.rank = len(ufc_finite_element_classnames) - self.num_coefficients
        self.name = name
        self.coefficient_names = coefficient_names
        self.ufc_form_classname = ufc_form_classname
        self.ufc_finite_element_classnames = ufc_finite_element_classnames
        self.ufc_dofmap_classnames = ufc_dofmap_classnames
        self.ufc_coordinate_mapping_classnames = ufc_coordinate_mapping_classnames

    def __str__(self):
        s = "UFCFormNames instance:\n"
        s += "rank:                      %d\n" % self.rank
        s += "num_coefficients:          %d\n" % self.num_coefficients
        s += "name:                      %s\n" % self.name
        s += "coefficient_names:         %s\n" % str(self.coefficient_names)
        s += "ufc_form_classname:        %s\n" % str(self.ufc_form_classname)
        s += "finite_element_classnames: %s\n" % str(
            self.ufc_finite_element_classnames)
        s += "ufc_dofmap_classnames:    %s\n" % str(self.ufc_dofmap_classnames)
        s += "ufc_coordinate_mapping_classnames:    %s\n" % str(
            self.ufc_coordinate_mapping_classnames)
        return s


class UFCElementNames:

    "Encapsulation of the names related to a generated UFC element."

    def __init__(self, name, ufc_finite_element_classnames,
                 ufc_dofmap_classnames, ufc_coordinate_mapping_classnames):
        """Arguments:

        """
        assert len(ufc_finite_element_classnames) == len(ufc_dofmap_classnames)
        assert len(ufc_finite_element_classnames) == len(
            ufc_coordinate_mapping_classnames)

        self.name = name
        self.ufc_finite_element_classnames = ufc_finite_element_classnames
        self.ufc_dofmap_classnames = ufc_dofmap_classnames
        self.ufc_coordinate_mapping_classnames = ufc_coordinate_mapping_classnames

    def __str__(self):
        s = "UFCFiniteElementNames instance:\n"
        s += "name:                      {}\n".format(self.name)
        s += "finite_element_classnames: {}\n".format(
            self.ufc_finite_element_classnames)
        s += "ufc_dofmap_classnames:     {}\n".format(
            self.ufc_dofmap_classnames)
        s += "ufc_coordinate_mapping_classnames: {}\n".format(
            self.ufc_dofmap_classnames)
        return s
