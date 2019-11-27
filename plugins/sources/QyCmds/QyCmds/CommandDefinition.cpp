#include "CommandDefinition.h"

#include "QmSkinSetWeights.h"

namespace {
	std::vector<CommandCreation> commands_ = {
		{ QmSkinSetWeights::Name(), QmSkinSetWeights::Creator },
	};
}

const std::vector<CommandCreation>& ListCommands() {
	return commands_;
}
