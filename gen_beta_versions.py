TEMPLATE = r"""
        /** v1.{ver}.0 */
        V1_{ver}_0,"""

for version in range(26, 36):
    print(TEMPLATE.format(ver=version))
