#pragma once

struct CommandCreation {
	MString name;
	MCreatorFunction creator;
};

const std::vector<CommandCreation>& ListCommands();
