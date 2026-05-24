backend\app\domain\astrology\builders\chart_object_runtime_builder.py:19:    ChartObjectCapabilities,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:27:    ChartObjectType,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:155:                object_type=ChartObjectType.LUMINARY if is_luminary else ChartObjectType.PLANET,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:167:                capabilities=ChartObjectCapabilities(
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:168:                    supports_aspects=True,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:169:                    supports_dignities=True,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:170:                    supports_house_position=True,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:171:                    supports_fixed_star_conjunction=True,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:172:                    supports_motion=motion_payload is not None,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:173:                    supports_visibility=visibility_payload is not None,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:174:                    supports_interpretation=True,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:175:                    supports_dominance=True,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:176:                    supports_rulership=True,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:301:                object_type=ChartObjectType.ASTRAL_POINT,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:313:                capabilities=ChartObjectCapabilities(
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:314:                    supports_aspects=include_astral_points_in_aspects,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:315:                    supports_house_position=point.house is not None,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:316:                    supports_interpretation=True,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:346:                object_type=ChartObjectType.ANGLE,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:355:                capabilities=ChartObjectCapabilities(
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:356:                    supports_aspects=include_angles_in_aspects,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:357:                    supports_house_position=True,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:358:                    supports_interpretation=True,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:383:            object_type=ChartObjectType.HOUSE_CUSP,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:392:            capabilities=ChartObjectCapabilities(supports_house_position=True),
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:425:                object_type=ChartObjectType.FIXED_STAR,
backend\app\domain\astrology\builders\chart_object_runtime_builder.py:434:                capabilities=ChartObjectCapabilities(),
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:20:class ChartObjectType(StrEnum):
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:72:class ChartObjectCapabilities:
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:75:    supports_aspects: bool = False
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:76:    supports_dignities: bool = False
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:77:    supports_house_position: bool = False
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:78:    supports_visibility: bool = False
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:79:    supports_motion: bool = False
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:80:    supports_interpretation: bool = False
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:81:    supports_dominance: bool = False
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:82:    supports_rulership: bool = False
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:83:    supports_fixed_star_conjunction: bool = False
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:391:    object_type: ChartObjectType
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:397:    capabilities: ChartObjectCapabilities
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:411:    capabilities: ChartObjectCapabilities,
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:416:        (capabilities.supports_motion, payloads.motion, "motion"),
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:417:        (capabilities.supports_visibility, payloads.visibility, "visibility"),
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:418:        (capabilities.supports_house_position, payloads.house_position, "house_position"),
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:432:    capabilities: ChartObjectCapabilities,
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:436:    if not capabilities.supports_dignities and payloads.dignity is not None:
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:441:    capabilities: ChartObjectCapabilities,
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:445:    if not capabilities.supports_dominance and payloads.dominance is not None:
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:450:    capabilities: ChartObjectCapabilities,
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:454:    if not capabilities.supports_rulership and payloads.rulership is not None:
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:459:    capabilities: ChartObjectCapabilities,
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:463:    if not capabilities.supports_fixed_star_conjunction and payloads.fixed_star_conjunctions:
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:471:        capability_name="supports_dignities",
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:480:        capability_name="supports_dominance",
backend\app\domain\astrology\runtime\chart_object_runtime_data.py:489:        capability_name="supports_rulership",
