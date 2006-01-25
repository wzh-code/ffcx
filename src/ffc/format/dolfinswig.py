"DOLFIN-SWIG output format."

__author__ = "Anders Logg (logg@tti-c.org)"
__date__ = "2004-10-14 -- 2005-11-30"
__copyright__ = "Copyright (c) 2004, 2005 Anders Logg"
__license__  = "GNU GPL Version 2"

# FFC common modules
from ffc.common.constants import *
from ffc.common.util import *

# FFC compiler modules
from ffc.compiler.mixedelement import *

#from ffc.compiler.finiteelement import *

# FFC format modules
import xml

# Specify formatting for code generation
format = { "sum": lambda l: " + ".join(l),
           "subtract": lambda l: " - ".join(l),
           "multiplication": lambda l: "*".join(l),
           "grouping": lambda s: "(%s)" % s,
           "determinant": "map.det",
           "floating point": lambda a: "%.15e" % a,
           "constant": lambda j: "c%d" % j,
           "coefficient table": lambda j, k: "c[%d][%d]" % (j, k),
           "coefficient": lambda j, k: "c%d_%d" % (j, k),
           "transform": lambda j, k: "map.g%d%d" % (j, k),
           "reference tensor" : lambda j, i, a: None,
           "geometry tensor": lambda j, a: "G%d_%s" % (j, "_".join(["%d" % index for index in a])),
           "element tensor": lambda i, k: "block[%d]" % k }

def init(options):
    "Initialize code generation for DOLFIN-SWIG format."

    # Don't generate code for element tensor in BLAS mode
    if options["blas"]:
        format["element tensor"] = lambda i, k: None
    else:
        format["element tensor"] = lambda i, k: "block[%d]" % k

    return

def write(forms, options):
    "Generate code for DOLFIN-SWIG format."
    print "\nGenerating output for DOLFIN-SWIG"

    # Get name of form
    name = forms[0].name

    # Write file header
    output = ""
    output += __file_header(name, options)

    # Write all forms
    for j in range(len(forms)):
        form = forms[j]

        # Choose class names
        if form.rank == 1:
            type = "Linear"
        elif form.rank == 2:
            type = "Bilinear"
        else:
            print """DOLFIN can only handle linear or bilinear forms.
I will try to generate the multi-linear form but you will not
be able to use it with DOLFIN."""
            type = "Multilinear"

        # Compute name of XML data file (if any)
        if len(forms) > 1:
            xmlfile = "%s-%d.xml" % (forms[j].name, j)
        else:
            xmlfile = "%s.xml" % forms[j].name

        # Write form
        output += __form(form, type, options, xmlfile)

    # Write file footer
    output += __file_footer()

    # Write file
    filename = name + ".h"
    file = open(filename, "w")
    file.write(output)
    file.close()
    print "Output written to " + filename

    # Write XML files if compiling for BLAS
    if options["blas"]:
        print ""
        print "Generating data files for DOLFIN BLAS format"
        xml.write(forms, options)
    
    return

def __file_header(name, options):
    "Generate file header for DOLFIN."

    # Check if we should use the GPL
    if options["no-gpl"]:
        license = ""
    else:
        license = "// Licensed under the %s.\n" % FFC_LICENSE        

    # Check if we should compile with BLAS option
    if options["blas"]:
        blasinclude = "\n#include <cblas.h>\n"
    else:
        blasinclude = ""
        
    return """\
// Automatically generated by FFC, the FEniCS Form Compiler, version %s.
// For further information, go to http://www/fenics.org/ffc/.
%s
#ifndef __%s_H
#define __%s_H
%s
#include <dolfin/Mesh.h>
#include <dolfin/Cell.h>
#include <dolfin/Point.h>
#include <dolfin/Vector.h>
#include <dolfin/AffineMap.h>
#include <dolfin/FiniteElement.h>
#include <dolfin/LinearForm.h>
#include <dolfin/BilinearForm.h>

namespace dolfin {

""" % (FFC_VERSION, license, capall(name), capall(name), blasinclude)

def __file_footer():
    "Generate file footer for DOLFIN."
    return """}

#endif\n"""

def __elements(form, subclass):
    "Generate finite elements for DOLFIN."

    output = ""
    
    # Write test element (if any)
    if form.test:
        output += __element(form.test, form.name + subclass + "TestElement")

    # Write trial element (if any)
    if form.trial:
        output += __element(form.trial, form.name + subclass + "TrialElement")

    # Write function elements (if any)
    for j in range(len(form.elements)):
        output += __element(form.elements[j], form.name + subclass + "FunctionElement_%d" % j)
    
    return output

def __element(element, name):
    "Generate finite element for DOLFIN."

    # Generate code for initialization of tensor dimensions
    if element.rank() > 0:
        diminit = "    tensordims = new unsigned int [%d];\n" % element.rank()
        for j in range(element.rank()):
            diminit += "    tensordims[%d] = %d;\n" % (j, element.tensordim(j))
    else:
        diminit = "    // Element is scalar, don't need to initialize tensordims\n"

    # Generate code for initializaton of sub elements
    if isinstance(element, MixedElement):
        elementinit = "    subelements = new FiniteElement* [%d];\n" % len(element.elements)
        for j in range(len(element.elements)):
            elementinit += "    subelements[%d] = new SubElement_%d();\n" % (j, j)
    else:
        elementinit = "    // Element is simple, don't need to initialize subelements\n"
        
    # Generate code for tensordim function
    if element.rank() > 0:
        tensordim = "dolfin_assert(i < %d);\n    return tensordims[i];" % element.rank()
    else:
        tensordim = 'dolfin_error("Element is scalar.");\n    return 0;'

    # Generate code for dofmap()
    dofmap = ""
    for declaration in element.dofmap.declarations:
        dofmap += "    %s = %s;\n" % (declaration.name, declaration.value)
    
    # Generate code for pointmap()
    pointmap = ""
    for declaration in element.pointmap.declarations:
        pointmap += "    %s = %s;\n" % (declaration.name, declaration.value)

    # Generate code for vertexeval()
    vertexeval = ""
    for declaration in element.vertexeval.declarations:
        vertexeval += "    %s = %s;\n" % (declaration.name, declaration.value)

    # Generate code for operator[] and compute elementdim
    if isinstance(element, MixedElement):
        indexoperator = "    return *subelements[i];\n"
        elementdim = len(element.elements)
    else:
        indexoperator = "    return *this;\n"
        elementdim = 1

    # Generate code for sub elements of mixed elements
    subelements = ""
    if isinstance(element, MixedElement):
        for i in range(len(element.elements)):
            subelements += __element(element.elements[i], "SubElement_%d" % i)
    
    # Generate output
    output = """\

class %s : public dolfin::FiniteElement
{
public:

  %s() : dolfin::FiniteElement(), tensordims(0), subelements(0)
  {
%s
%s  }

  ~%s()
  {
    if ( tensordims ) delete [] tensordims;
    if ( subelements )
    {
      for (unsigned int i = 0; i < elementdim(); i++)
        delete subelements[i];
      delete [] subelements;
    }
  }

  inline unsigned int spacedim() const
  {
    return %d;
  }

  inline unsigned int shapedim() const
  {
    return %d;
  }

  inline unsigned int tensordim(unsigned int i) const
  {
    %s
  }

  inline unsigned int elementdim() const
  {
    return %d;
  }

  inline unsigned int rank() const
  {
    return %d;
  }

  void dofmap(int dofs[], const Cell& cell, const Mesh& mesh) const
  {
%s  }

  void pointmap(Point points[], unsigned int components[], const AffineMap& map) const
  {
%s  }

  void vertexeval(real values[], unsigned int vertex, const real x[], const Mesh& mesh) const
  {
    // FIXME: Temporary fix for Lagrange elements
%s  }

  const FiniteElement& operator[] (unsigned int i) const
  {
%s  }

  FiniteElement& operator[] (unsigned int i)
  {
%s  }
  
private:
%s
  unsigned int* tensordims;
  FiniteElement** subelements;

};
""" % (name, name,
       diminit,
       elementinit,
       name,
       element.spacedim(),
       element.shapedim(),
       tensordim,
       elementdim,
       element.rank(),
       dofmap,
       pointmap,
       vertexeval,
       indexoperator,
       indexoperator,
       subelements)

    return indent(output, 2)

def __form(form, type, options, xmlfile):
    "Generate form for DOLFIN."
    
    #ptr = "".join(['*' for i in range(form.rank)])
    subclass = type + "Form"
    baseclass = type + "Form"

    # Create argument list for form (functions and constants)
    arguments = ", ".join([("Function& w%d" % j) for j in range(form.nfunctions)] + \
                          [("const real& c%d" % j) for j in range(form.nconstants)])

    # Create initialization list for constants (if any)
    constinit = ", ".join([("c%d(c%d)" % (j, j)) for j in range(form.nconstants)])
    if constinit:
        constinit = ", " + constinit
    
    # Write elements
    output = __elements(form, subclass)
    
    # Write class header
    output += """\
/// This class contains the form to be evaluated, including
/// contributions from the interior and boundary of the domain.

class %s : public dolfin::%s
{
public:
""" % (form.name + subclass, baseclass)

    # Write constructor
    output += """\

  %s(%s) : dolfin::%s(%d)%s
  {
""" % (form.name + subclass, arguments, baseclass, form.nfunctions, constinit)

    # Initialize test and trial elements
    if form.test:
        output += """\
    // Create finite element for test space
    _test = new %sTestElement();
""" % (form.name + subclass)
    if form.trial:
        output += """\

    // Create finite element for trial space
    _trial = new %sTrialElement();
""" % (form.name + subclass)
        
    # Add functions (if any)
    if form.nfunctions > 0:
        output += """\

    // Add functions\n"""
        for j in range(form.nfunctions):
            output += "    add(w%d, new %sFunctionElement_%d());\n" % (j, form.name + subclass, j)

    # Initialize BLAS array (if any)
    if options["blas"]:
        output += """\

    // Initialize form data for BLAS
    blas.init(\"%s\");\n""" % xmlfile

    output += "  }\n"

    # Interior contribution (if any)
    if form.AKi.terms:
        eval = __eval_interior(form, options)
        output += """\

  void eval(real block[], const AffineMap& map) const
  {
%s  }
""" % eval

    # Boundary contribution (if any)
    if form.AKb.terms:
        eval = __eval_boundary(form, options)
        output += """\

  void eval(real block[], const AffineMap& map, unsigned int boundary) const
  {
%s  }
""" % eval

    # Declare class members (if any)
    if form.nconstants > 0:
        output += """\

private:

"""

    # Create declaration list for for constants (if any)
    if form.nconstants > 0:
        for j in range(form.nconstants):
            output += """\
  const real& c%d;""" % j
        output += "\n"

    # Class footer
    output += """
};

"""

    return output

def __eval_interior(form, options):
    "Generate function eval() for DOLFIN, interior part."
    if options["blas"]:
        return __eval_interior_blas(form, options)
    else:
        return __eval_interior_default(form, options)

def __eval_interior_default(form, options):
    "Generate function eval() for DOLFIN, interior part (default version)."
    output = ""

    if not options["debug-no-geometry-tensor"]:
        if len(form.cK) > 0:
            output += """\
    // Compute coefficients
%s
""" % "".join(["    const real %s = %s;\n" % (cK.name, cK.value) for cK in form.cK if cK.used])
        output += """\
    // Compute geometry tensors
%s"""  % "".join(["    const real %s = %s;\n" % (gK.name, gK.value) for gK in form.AKi.gK if gK.used])
    else:
        output += """\
    // Compute geometry tensors
%s""" % "".join(["    const real %s = 0.0;\n" % gK.name for gK in form.AKi.gK if gK.used])

    if not options["debug-no-element-tensor"]:
        output += """\

    // Compute element tensor
%s""" % "".join(["    %s = %s;\n" % (aK.name, aK.value) for aK in form.AKi.aK])

    return output

def __eval_interior_blas(form, options):
    "Generate function eval() for DOLFIN, interior part (BLAS version)."
    output = ""

    # Compute geometry tensors
    if not options["debug-no-geometry-tensor"]:
        if len(form.cK) > 0:
            output += """\
    // Compute coefficients
%s
""" % "".join(["    const real %s = %s;\n" % (cK.name, cK.value) for cK in form.cK if cK.used])
        output += """\
    // Reset geometry tensors
    for (unsigned int i = 0; i < blas.ni; i++)
      blas.Gi[i] = 0.0;

    // Compute entries of G multiplied by nonzero entries of A
%s
""" % "".join(["    blas.Gi[%d] = %s;\n" % (j, form.AKi.gK[j].value)
               for j in range(len(form.AKi.gK)) if form.AKi.gK[j].used])

    # Compute element tensor
    if not options["debug-no-element-tensor"]:
        output += """\
    // Compute element tensor using level 2 BLAS
    cblas_dgemv(CblasRowMajor, CblasNoTrans, blas.mi, blas.ni, 1.0, blas.Ai, blas.ni, blas.Gi, 1, 0.0, block, 1);
"""

    return output

def __eval_boundary(form, options):
    "Generate function eval() for DOLFIN, boundary part."
    if options["blas"]:
        return __eval_boundary_blas(form, options)
    else:
        return __eval_boundary_default(form, options)

def __eval_boundary_default(form, options):
    "Generate function eval() for DOLFIN, boundary part (default version)."
    output = ""
    
    if not options["debug-no-geometry-tensor"]:
        if len(form.cK) > 0:
            output += """\
    // Compute coefficients
%s
""" % "".join(["    const real %s = %s;\n" % (cK.name, cK.value) for cK in form.cK if cK.used])
        output += """\
    // Compute geometry tensors
%s""" % "".join(["    const real %s = %s;\n" % (gK.name, gK.value) for gK in form.AKb.gK if gK.used])
    else:
        output += """\
    // Compute geometry tensors
%s""" % "".join(["    const real %s = 0.0;\n" % gK.name for gK in form.AKi.gK if gK.used])

    if not options["debug-no-element-tensor"]:
        output += """\

    // Compute element tensor
%s""" % "".join(["    %s = %s;\n" % (aK.name, aK.value) for aK in form.AKb.aK])

    return output

def __eval_boundary_blas(form, options):
    "Generate function eval() for DOLFIN, boundary part (default version)."
    output = ""

    # Compute geometry tensors
    if not options["debug-no-geometry-tensor"]:
        if len(form.cK) > 0:
            output += """\
    // Compute coefficients
%s
""" % "".join(["    const real %s = %s;\n" % (cK.name, cK.value) for cK in form.cK if cK.used])        
        output += """\
    // Reset geometry tensors
    for (unsigned int i = 0; i < blas.nb; i++)
      blas.Gb[i] = 0.0;

    // Compute entries of G multiplied by nonzero entries of A
%s
""" % "".join(["    blas.Gb[%d] = %s;\n" % (j, form.AKb.gK[j].value)
                for j in range(len(form.AKb.gK)) if form.AKb.gK[j].used])

    # Compute element tensor
    if not options["debug-no-element-tensor"]:
        output += """\
    // Compute element tensor using level 2 BLAS
    cblas_dgemv(CblasRowMajor, CblasNoTrans, blas.mb, blas.nb, 1.0, blas.Ab, blas.nb, blas.Gb, 1, 0.0, block, 1);
"""

    return output
