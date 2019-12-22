#include "CommandDefinition.h"

MStatus initializePlugin(MObject obj) {
	MFnPlugin plugin(obj, "@hal1932", "1.0", "any");

	for (const auto& item : ListCommands()) {
		plugin.registerCommand(item.name, item.creator);
	}

	return MStatus::kSuccess;
}

MStatus uninitializePlugin(MObject obj) {
	MFnPlugin plugin(obj);

	for (const auto& item : ListCommands()) {
		plugin.deregisterCommand(item.name);
	}

	return MStatus::kSuccess;
}
