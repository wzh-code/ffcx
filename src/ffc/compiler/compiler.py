"""This is the compiler, taking a multi-linear form expressed as a Sum
and building the data structures (geometry and reference tensors) for
the evaluation of the multi-linear form."""

__author__ = "Anders Logg (logg@tti-c.org)"
__date__ = "2004-11-17 -- 2005-11-15"
__copyright__ = "Copyright (c) 2004, 2005 Anders Logg"
__license__  = "GNU GPL Version 2"

# Python modules
import sys
from sets import Set # (Could use built-in set with Python 2.4)

# FFC common modules
from ffc.common.debug import *
from ffc.common.constants import *
from ffc.common.exceptions import *

# FFC format modules
sys.path.append("../../")
from ffc.format import dolfin
from ffc.format import dolfinswig
from ffc.format import latex
from ffc.format import raw
from ffc.format import ase
from ffc.format import xml

# FFC compiler modules
from form import *
from index import *
from tokens import *
from algebra import *
from operators import *
from signature import *
from elementsearch import *
from finiteelement import *
from mixedelement import *
from elementtensor import *
from projection import *

def compile(sums, name = "Form", language = FFC_LANGUAGE, options = FFC_OPTIONS):
    """Compile variational form(s). This function takes as argument a
    Sum or a list of Sums representing the multilinear form(s). The
    return value is a Form or a list of Forms. Calling this function
    is equivalent to first calling build() followed by write()."""

    # Add default values for any missing options
    for key in FFC_OPTIONS:
        if not key in options:
            options[key] = FFC_OPTIONS[key]

    # Build data structures
    forms = build(sums, name, language, options)

    # Generate code
    if not forms == None:
        write(forms, options)

    return forms

def build(sums, name = "Form", language = FFC_LANGUAGE, options = FFC_OPTIONS):
    "Build data structures for evaluation of the variational form(s)."

    # Add default values for any missing options
    for key in FFC_OPTIONS:
        if not key in options:
            options[key] = FFC_OPTIONS[key]

    # Create a Form from the given sum(s)
    if isinstance(sums, list):
        forms = [Form(Sum(sum), name) for sum in sums if not sum == None]
    else:
        forms = [Form(Sum(sums), name)]

    # Check that the list is not empty
    if not len(forms) > 0:
        print "No forms specified, nothing to do."
        return None

    # Choose language
    if not language:
        format = dolfin
    elif language == "dolfin" or language == "DOLFIN":
        format = dolfin
    elif language == "dolfin-swig" or language == "DOLFIN-SWIG":
        format = dolfinswig
    elif language == "latex" or language == "LaTeX":
        format = latex
    elif language == "raw":
        format = raw
    elif language == "ase":
        format = ase
    elif language == "xml":
        format = xml
    else:
        raise "RuntimeError", "Unknown language " + str(language)

    # Initialize format
    format.init(options)

    # Generate the element tensor for all given forms
    for form in forms:

        debug("\nCompiling form: " + str(form), 0)
        debug("Number of terms in form: %d" % len(form.sum.products), 1)
        
        # Count the number of functions
        form.nfunctions = max_index(form.sum, "function") + 1
        debug("Number of functions (coefficients): " + str(form.nfunctions), 1)

        # Count the number of projections
        form.nprojections = max_index(form.sum, "projection") + 1
        debug("Number of projections (coefficients): " + str(form.nprojections), 1)

        # Count the number of constants
        form.nconstants = max_index(form.sum, "constant") + 1
        debug("Number of constants: " + str(form.nconstants), 1)

        # Find the test and trial finite elements
        form.test = find_test(form.sum)
        form.trial = find_trial(form.sum)

        # Find the original elements for all functions
        form.elements = find_elements(form.sum, form.nfunctions)

        # Find the projections for all functions
        form.projections = find_projections(form.sum, form.nprojections)

        # Create empty set of used coefficient declarations
        cK_used = Set()

        # Create element tensors
        print "Compiling tensor representation for interior"
        form.AKi = ElementTensor(form.sum, "interior", format, cK_used)
        print "Compiling tensor representation for boundary"
        form.AKb = ElementTensor(form.sum, "boundary", format, cK_used)

        # Compute coefficient declarations
        form.cK = __compute_coefficients(form.projections, format, cK_used)

        # Check primary ranks
        __check_primary_ranks(form)

        # Save format
        form.format = format

    # Return form
    if len(forms) > 1:
        return forms
    else:
        return forms[0]

def write(forms, options = FFC_OPTIONS):
    "Generate code from previously built data structures."

    # Add default values for any missing options
    for key in FFC_OPTIONS:
        if not key in options:
            options[key] = FFC_OPTIONS[key]

    # Make sure we have a list of forms
    if isinstance(forms, list):
        forms = [form for form in forms if not form == None]
    elif not forms == None:
        forms = [forms]
    else:
        forms = []

    # Check that the list is not empty
    if not len(forms) > 0:
        print "No forms specified, nothing to do."
        return None

    # Generate output (all forms have the same format)
    forms[0].format.write(forms, options)

    return

def __check_primary_ranks(form):
    "Check that all primary ranks are equal."
    terms = form.AKi.terms + form.AKb.terms
    ranks = [term.A0.i.rank for term in terms]
    if not ranks[1:] == ranks[:-1]:
        "Form must be linear in each of its arguments."
    form.rank = ranks[0]
    form.dims = terms[0].A0.i.dims
    form.indices = terms[0].A0.i.indices
    return

def __compute_coefficients(projections, format, cK_used):
    "Precompute declarations of coefficients according to given format."

    declarations = []

    # Iterate over projections
    for (n0, n1, e0, e1, P) in projections:

        if P == None:
            # No projection, just copy the values
            for k in range(e0.spacedim()):
                name = format.format["coefficient"](n1, k)
                value = format.format["coefficient table"](n0, k)
                declaration = Declaration(name, value)
                # Mark entries that are used
                if name in cK_used:
                    declaration.used = True
                declarations += [declaration]
        else:
            # Compute projection
            (m, n) = Numeric.shape(P)
            for k in range(m):
                terms = []
                for l in range(n):
                    if abs(P[k][l] < FFC_EPSILON):
                        continue
                    cl = format.format["coefficient table"](n0, l)
                    if abs(P[k][l] - 1.0) < FFC_EPSILON:
                        terms += [cl]
                    else:
                        Pkl = format.format["floating point"](P[k][l])
                        terms += [format.format["multiplication"]([Pkl, cl])]
                name = format.format["coefficient"](n1, k)
                value = format.format["sum"](terms)
                declaration = Declaration(name, value)
                # Mark entries that are used
                if name in cK_used:
                    declaration.used = True
                # Add to list of declarations
                declarations += [declaration]

    return declarations

if __name__ == "__main__":

    print "Testing form compiler"
    print "---------------------"

    element = FiniteElement("Lagrange", "triangle", 1)
    
    u = BasisFunction(element)
    v = BasisFunction(element)
    i = Index()
    dx = Integral("interior")
    ds = Integral("boundary")
    
    a = u.dx(i)*v.dx(i)*dx + u*v*ds
    compile(a, "form", "C++")
    compile(a, "form", "LaTeX")
    compile(a, "form", "raw")
