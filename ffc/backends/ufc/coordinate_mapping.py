# -*- coding: utf-8 -*-
# Code generation format strings for UFC (Unified Form-assembly Code)
# This code is released into the public domain.
#
# The FEniCS Project (http://www.fenicsproject.org/) 2006-2017

ufc_coordinate_mapping_combined = """
struct {factory_name}
{{
}};
"""


coordinate_mapping_combined = """
class %(classname)s: public ufc::coordinate_mapping
{%(members)s
public:

  %(classname)s(%(constructor_arguments)s) : ufc::coordinate_mapping()%(initializer_list)s
  {
%(constructor)s
  }

  ~%(classname)s() override
  {
%(destructor)s
  }

  const char * signature() const final override
  {
%(signature)s
  }

  ufc::coordinate_mapping * create() const final override
  {
%(create)s
  }

  int64_t geometric_dimension() const final override
  {
%(geometric_dimension)s
  }

  int64_t topological_dimension() const final override
  {
%(topological_dimension)s
  }

  ufc::shape cell_shape() const final override
  {
%(cell_shape)s
  }

  ufc_finite_element * create_coordinate_finite_element() const final override
  {
%(create_coordinate_finite_element)s
  }

  ufc_dofmap * create_coordinate_dofmap() const final override
  {
%(create_coordinate_dofmap)s
  }

  void compute_physical_coordinates(
      double * x, int64_t num_points,
      const double * X,
      const double * coordinate_dofs) const final override
  {
%(compute_physical_coordinates)s
  }

  void compute_reference_coordinates(
      double * X, int64_t num_points,
      const double * x,
      const double * coordinate_dofs, int cell_orientation) const final override
  {
%(compute_reference_coordinates)s
  }

  void compute_reference_geometry(
      double * X, double * J, double * detJ, double * K, int64_t num_points,
      const double * x,
      const double * coordinate_dofs, int cell_orientation) const final override
  {
%(compute_reference_geometry)s
  }

  void compute_jacobians(
      double * J, int64_t num_points,
      const double * X,
      const double * coordinate_dofs) const final override
  {
%(compute_jacobians)s
  }

  void compute_jacobian_determinants(
      double * detJ, int64_t num_points,
      const double * J,
      int cell_orientation) const final override
  {
%(compute_jacobian_determinants)s
  }

  void compute_jacobian_inverses(
      double * K, int64_t num_points,
      const double * J, const double * detJ) const final override
  {
%(compute_jacobian_inverses)s
  }

  void compute_geometry(
      double * x, double * J, double * detJ, double * K, int64_t num_points,
      const double * X,
      const double * coordinate_dofs, int cell_orientation) const final override
  {
%(compute_geometry)s
  }

  void compute_midpoint_geometry(
      double * x, double * J,
      const double * coordinate_dofs) const final override
  {
%(compute_midpoint_geometry)s
  }

};
"""


coordinate_mapping_header = """
class %(classname)s: public ufc::coordinate_mapping
{%(members)s
public:

  %(classname)s(%(constructor_arguments)s);

  ~%(classname)s() override;

  const char * signature() const final override;

  ufc::coordinate_mapping * create() const final override;

  int64_t geometric_dimension() const final override;

  int64_t topological_dimension() const final override;

  ufc::shape cell_shape() const final override;

  ufc_finite_element * create_coordinate_finite_element() const final override;

  ufc_dofmap * create_coordinate_dofmap() const final override;

  void compute_physical_coordinates(
      double * x, int64_t num_points,
      const double * X,
      const double * coordinate_dofs) const final override;

  void compute_reference_coordinates(
      double * X, int64_t num_points,
      const double * x,
      const double * coordinate_dofs, int cell_orientation) const final override;

  void compute_reference_geometry(
      double * X, double * J, double * detJ, double * K, int64_t num_points,
      const double * x,
      const double * coordinate_dofs, int cell_orientation) const final override;

  void compute_jacobians(
      double * J, int64_t num_points,
      const double * X,
      const double * coordinate_dofs) const final override;

  void compute_jacobian_determinants(
      double * detJ, int64_t num_points,
      const double * J,
      int cell_orientation) const final override;

  void compute_jacobian_inverses(
      double * K, int64_t num_points,
      const double * J, const double * detJ) const final override;

  void compute_geometry(
      double * x, double * J, double * detJ, double * K, int64_t num_points,
      const double * X,
      const double * coordinate_dofs, int cell_orientation) const final override;

  void compute_midpoint_geometry(
      double * x, double * J,
      const double * coordinate_dofs) const final override;

};
"""


coordinate_mapping_implementation = """
%(classname)s::%(classname)s(%(constructor_arguments)s) : ufc::coordinate_mapping()%(initializer_list)s
{
%(constructor)s
}

%(classname)s::~%(classname)s()
{
%(destructor)s
}

const char * %(classname)s::signature() const
{
%(signature)s
}

ufc::coordinate_mapping * %(classname)s::create() const
{
%(create)s
}

int64_t %(classname)s::geometric_dimension() const
{
%(geometric_dimension)s
}

int64_t %(classname)s::topological_dimension() const
{
%(topological_dimension)s
}

ufc::shape %(classname)s::cell_shape() const
{
%(cell_shape)s
}

ufc_finite_element * %(classname)s::create_coordinate_finite_element() const
{
%(create_coordinate_finite_element)s
}

ufc_dofmap * %(classname)s::create_coordinate_dofmap() const
{
%(create_coordinate_dofmap)s
}

void %(classname)s::compute_physical_coordinates(
    double * x, int64_t num_points,
    const double * X,
    const double * coordinate_dofs) const
{
%(compute_physical_coordinates)s
}

void %(classname)s::compute_reference_coordinates(
    double * X, int64_t num_points,
    const double * x,
    const double * coordinate_dofs, int cell_orientation) const
{
%(compute_reference_coordinates)s
}

void %(classname)s::compute_reference_geometry(
    double * X, double * J, double * detJ, double * K, int64_t num_points,
    const double * x,
    const double * coordinate_dofs, int cell_orientation) const
{
%(compute_reference_geometry)s
}

void %(classname)s::compute_jacobians(
    double * J, int64_t num_points,
    const double * X,
    const double * coordinate_dofs) const
{
%(compute_jacobians)s
}

void %(classname)s::compute_jacobian_determinants(
    double * detJ, int64_t num_points,
    const double * J,
    int cell_orientation) const
{
%(compute_jacobian_determinants)s
}

void %(classname)s::compute_jacobian_inverses(
    double * K, int64_t num_points,
    const double * J, const double * detJ) const
{
%(compute_jacobian_inverses)s
}

void %(classname)s::compute_geometry(
    double * x, double * J, double * detJ, double * K, int64_t num_points,
    const double * X,
    const double * coordinate_dofs, int cell_orientation) const
{
%(compute_geometry)s
}

void %(classname)s::compute_midpoint_geometry(
    double * x, double * J,
    const double * coordinate_dofs) const
{
%(compute_midpoint_geometry)s
}
"""
