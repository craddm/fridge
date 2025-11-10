import pulumi
import pulumi_openstack as openstack

test_server = openstack.compute.Instance(
    "test-server",
    image_name="Ubuntu-Noble-24.04-20250313",
    flavor_name="vm.v1.tiny",
)
