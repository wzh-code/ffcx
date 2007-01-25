"Code generation for the UFC 1.0 format."

__author__ = "Anders Logg (logg@simula.no)"
__date__ = "2007-01-08 -- 2007-01-24"
__copyright__ = "Copyright (C) 2007 Anders Logg"
__license__  = "GNU GPL Version 2"

# FFC common modules
from ffc.common.util import *
from ffc.common.debug import *
from ffc.common.constants import *

# FFC fem modules
from ffc.fem.finiteelement import *

# FFC format modules
from ufc import *

# Specify formatting for code generation
format = { "add": lambda l: " + ".join(l),
           "sum": lambda l: " + ".join(l), # FIXME: Remove
           "subtract": lambda l: " - ".join(l),
           "multiply": lambda l: "*".join(l),
           "multiplication": lambda l: "*".join(l), # FIXME: Remove
           "grouping": lambda s: "(%s)" % s,
           "determinant": "det",
           "floating point": lambda a: "%.15e" % a,
           "constant": lambda j: "c%d" % j,
           "coefficient table": lambda j, k: "c[%d][%d]" % (j, k),
           "coefficient": lambda j, k: "c%d_%d" % (j, k),
           "transform": lambda j, k, r: "%s.g%d%d" % (r, j, k),
           "reference tensor" : lambda j, i, a: None,
           "geometry tensor": lambda j, a: "G%d_%s" % (j, "_".join(["%d" % index for index in a])),
           "element tensor": lambda i, k: "block[%d]" % k,
           "tmp declaration": lambda j, k: "const real tmp%d_%d" % (j, k),
           "tmp access": lambda j, k: "tmp%d_%d" % (j, k),
           ("entity", 2, 0) : lambda i : "cell.entities(0)[%d]" % i,
           ("entity", 2, 1) : lambda i : "cell.entities(1)[%d]" % i,
           ("entity", 2, 2) : lambda i : "cell.index()",
           ("entity", 2, 3) : lambda i : "not defined",
           ("entity", 3, 0) : lambda i : "cell.entities(0)[%d]" % i,
           ("entity", 3, 1) : lambda i : "cell.entities(1)[%d]" % i,
           ("entity", 3, 2) : lambda i : "cell.entities(2)[%d]" % i,
           ("entity", 3, 3) : lambda i : "cell.index()",
           ("num",    2, 0) : "mesh.topology().size(0)",
           ("num",    2, 1) : "mesh.topology().size(1)",
           ("num",    2, 2) : "mesh.topology().size(2)",
           ("num",    2, 3) : "not defined",
           ("num",    3, 0) : "mesh.topology().size(0)",
           ("num",    3, 1) : "mesh.topology().size(1)",
           ("num",    3, 2) : "mesh.topology().size(2)",
           ("num",    3, 3) : "mesh.topology().size(3)",
           ("check",  2, 0) : lambda i : "not defined",
           ("check",  2, 1) : lambda i : "cell.alignment(1, %d)" % i,
           ("check",  2, 2) : lambda i : "not defined",
           ("check",  2, 3) : lambda i : "not defined",
           ("check",  3, 0) : lambda i : "not defined",
           ("check",  3, 1) : lambda i : "cell.alignment(1, %d)" % i,
           ("check",  3, 2) : lambda i : "cell.alignment(2, %d)" % i,
           ("check",  3, 3) : lambda i : "not defined",
           "num_entities" : lambda dim : "m.num_entities[%d]" % dim}

def init(options):
    "Initialize code generation for the UFC 1.0 format."
    pass
    
def write(forms, code, options):
    "Generate code for the UFC 1.0 format."
    debug("Generating code for UFC 1.0")

    print "code = ", code

    for form in forms:
    
        # Set prefix
        prefix = form.name.lower()
        
        # Generate file header
        output = ""
        output += __generate_header(prefix, options)
        output += "\n"

        # Compute number of argument functions
        

        # Generate code for ufc::finite_element(s)
        for i in range(form.num_arguments):
            output += __generate_finite_element(form.finite_elements[i], code[("finite_element", i)], prefix, i, options)
            output += "\n"

        # Generate code for ufc::dof_map(s)
        for i in range(form.num_arguments):
            output += __generate_dof_map(code[("dof_map", i)], options, prefix, i)
            output += "\n"

        # Generate code for ufc::cell_integral
        output += __generate_cell_integral(prefix, options)
        output += "\n"

        # Generate code for ufc::exterior_facet_integral
        output += __generate_exterior_facet_integral(prefix, options)
        output += "\n"
        
        # Generate code for ufc::cell_integral
        output += __generate_interior_facet_integral(prefix, options)
        output += "\n"

        # Generate code for ufc::form
        output += __generate_form(form, prefix, options)
        output += "\n"
    
        # Generate code for footer
        output += __generate_footer(prefix, options)

        # Write file
        filename = "%s_ufc.h" % prefix
        file = open(filename, "w")
        file.write(output)
        file.close()
        debug("Output written to " + filename)

def __generate_header(prefix, options):
    "Generate file header"

    # Check if BLAS is required
    if options["blas"]:
        blas_include = "\n#include <cblas.h>"
        blas_warning = "\n// Warning: This code was generated with '-f blas' and requires cblas.h."
    else:
        blas_include = ""
        blas_warning = ""
        
    return """\
// This code conforms with the UFC specification version 1.0.
//
// This code was automatically generated by FFC version %s.%s

#ifndef __%s_H
#define __%s_H

#include <ufc.h>%s
""" % (FFC_VERSION, blas_warning, prefix.upper(), prefix.upper(), blas_include)

def __generate_footer(prefix, options):
    "Generate file footer"
    return """\
#endif
"""

def __generate_finite_element(finite_element, code, prefix, i, options):
    "Generate (modify) code for ufc::finite_element"

    ufc_code = {}

    # Set class name
    ufc_code["classname"] = "%s_finite_element_%d" % (prefix, i)

    # Generate code for members
    ufc_code["members"] = ""

    # Generate code for constructor
    ufc_code["constructor"] = "// Do nothing"

    # Generate code for destructor
    ufc_code["destructor"] = "// Do nothing"

    # Generate code for signature
    ufc_code["signature"] = "return \"%s\";" % code["signature"]

    # Generate code for cell_shape
    ufc_code["cell_shape"] = "return ufc::%s;" % shape_to_string[finite_element.cell_shape()]
    
    # Generate code for space_dimension
    ufc_code["space_dimension"] = "return %s;" % code["space_dimension"]

    # Generate code for value_rank
    ufc_code["value_rank"] = "return %s;" % code["value_rank"]

    # Generate code for value_dimension
    if finite_element.value_rank() == 0:
        body = "return %d;" % finite_element.value_dimension(0)
    else:
        body = "switch ( i )\n{\n"
        for i in range(finite_element.value_rank()):
            body += "case %d:\n  return %d;\n  break;\n" % finite_element.value_dimension(i)
        body += "default:\n  return 0;\n}"
    ufc_code["value_dimension"] = body

    # Generate code for evaluate_basis (FIXME: not implemented)
    ufc_code["evaluate_basis"] = "// Not implemented"

    # Generate code for evaluate_dof (FIXME: not implemented)
    ufc_code["evaluate_dof"] = "// Not implemented\nreturn 0.0;"

    # Generate code for inperpolate_vertex_values (FIXME: not implemented)
    ufc_code["interpolate_vertex_values"] = "// Not implemented"

    # Generate code for num_sub_elements
    ufc_code["num_sub_elements"] = "return %d;" % finite_element.num_sub_elements()

    # Generate code for sub_element
    if finite_element.num_sub_elements() == 1:
        body = "return new %s;" % ufc_code["classname"]
    else:
        body = "switch ( i )\n{\n"
        for i in range(finite_element.num_sub_elements()):
            body += "case %d:\n  return new %s_sub_element_%d();\n  break;\n" % (i, ufc_code["classname"], i)
        body += "default:\n  return 0;\n}"
    ufc_code["create_sub_element"] = body

    return __generate_code(finite_element_combined, ufc_code)

def __generate_dof_map(code, options, prefix, i):
    "Generate code for ufc::dof_map"

    ufc_code = {}

    # Set class name
    ufc_code["classname"] = "%s_dof_map_%d" % (prefix, i)

    # Generate code for members
    ufc_code["members"] = "\nprivate:\n\n  unsigned int __global_dimension;\n"

    # Generate code for constructor
    ufc_code["constructor"] = "__global_dimension = 0;"

    # Generate code for destructor
    ufc_code["destructor"] = "// Do nothing"

    # Generate code for signature
    ufc_code["signature"] = "return \"%s\";" % code["signature"]

    # Generate code for needs_mesh_entities
    ufc_code["needs_mesh_entities"] = "// Not implemented\nreturn true;"

    # Generate code for init_mesh
    ufc_code["init_mesh"] = "__global_dimension = %s;\nreturn false;" % code["global_dimension"]

    # Generate code for init_cell
    ufc_code["init_cell"] = "// Do nothing"

    # Generate code for init_cell_finalize
    ufc_code["init_cell_finalize"] = "// Do nothing"

    # Generate code for global_dimension
    ufc_code["global_dimension"] = "return __global_dimension;"

    # Generate code for local dimension
    ufc_code["local_dimension"] = "return %s;" % code["local_dimension"]

    # Generate code for num_facet_dofs
    ufc_code["num_facet_dofs"] = "// Not implemented\nreturn 0;"

    # Generate code for tabulate_dofs
    ufc_code["tabulate_dofs"] = "// Not implemented"

    # Generate code for tabulate_facet_dofs
    ufc_code["tabulate_facet_dofs"] = "// Not implemented"

    return __generate_code(dof_map_combined, ufc_code)

def __generate_cell_integral(prefix, options):
    "Generate code for ufc::cell_integral"

    code = {}

    # Set class name
    code["classname"] = "%s_cell_integral" % prefix

    # Generate code for members
    code["members"] = ""

    # Generate code for constructor
    code["constructor"] = "// Do nothing"

    # Generate code for destructor
    code["destructor"] = "// Do nothing"

    # Generate code for tabulate_tensor
    code["tabulate_tensor"] = "// Not implemented"
    
    return __generate_code(cell_integral_combined, code)

def __generate_exterior_facet_integral(prefix, options):
    "Generate code for ufc::exterior_facet_integral"

    code = {}

    # Set class name
    code["classname"] = "%s_exterior_facet_integral" % prefix

    # Generate code for members
    code["members"] = ""

    # Generate code for constructor
    code["constructor"] = "// Do nothing"

    # Generate code for destructor
    code["destructor"] = "// Do nothing"

    # Generate code for tabulate_tensor
    code["tabulate_tensor"] = "// Not implemented"
    
    return __generate_code(exterior_facet_integral_combined, code)

def __generate_interior_facet_integral(prefix, options):
    "Generate code for ufc::interior_facet_integral"

    code = {}

    # Set class name
    code["classname"] = "%s_interior_facet_integral" % prefix

    # Generate code for members
    code["members"] = ""

    # Generate code for constructor
    code["constructor"] = "// Do nothing"

    # Generate code for destructor
    code["destructor"] = "// Do nothing"

    # Generate code for tabulate_tensor
    code["tabulate_tensor"] = "// Not implemented"
    
    return __generate_code(interior_facet_integral_combined, code)

def __generate_form(form, prefix, options):
    "Generate code for ufc::form"

    code = {}

    # Set class name
    code["classname"] = prefix

    # Generate code for members
    code["members"] = ""

    # Generate code for constructor
    code["constructor"] = "// Do nothing"

    # Generate code for destructor
    code["destructor"] = "// Do nothing"

    # Generate code for signature
    code["signature"] = "return \"%s\";" % form.signature

    # Generate code for rank
    code["rank"] = "return %d;" % form.rank

    # Generate code for num_coefficients
    code["num_coefficients"] = "return %d;" % form.num_coefficients

    # Generate code for create_finite_element
    body = "switch ( i )\n{\n"
    for i in range(form.num_arguments):
        body += "case %d:\n  return new %s_finite_element_%d();\n  break;\n" % (i, prefix, i)
    body += "default:\n  return 0;\n}\n\nreturn 0;"
    code["create_finite_element"] = body

    # Generate code for create_dof_map
    body = "switch ( i )\n{\n"
    for i in range(form.num_arguments):
        body += "case %d:\n  return new %s_dof_map_%d();\n  break;\n" % (i, prefix, i)
    body += "default:\n  return 0;\n}\n\nreturn 0;"
    code["create_dof_map"] = body

    # Generate code for cell_integral
    code["create_cell_integral"] = "// Not implemented\nreturn 0;"

    # Generate code for exterior_facet_integral
    code["create_exterior_facet_integral"] = "// Not implemented\nreturn 0;"

    # Generate code for interior_facet_integral
    code["create_interior_facet_integral"] = "// Not implemented\nreturn 0;"

    return __generate_code(form_combined, code)

def __generate_code(format_string, code):
    "Generate code according to format string and code dictionary"
    # Fix indentation
    for key in code:
        if not key in ["classname", "members"]:
            code[key] = indent(code[key], 4)
    # Generate code
    return format_string % code
