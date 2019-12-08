#include "CommandDefinition.h"

#include "QmSkinSetWeights.h"
#include "QmBatchSetVertexColor.h"

namespace {
	std::vector<CommandCreation> commands_ = {
		{ QmSkinSetWeights::Name(), QmSkinSetWeights::Creator },
		{ QmBatchSetVertexColor::Name(), QmBatchSetVertexColor::Creator },
	};
}

const std::vector<CommandCreation>& ListCommands() {
	return commands_;
}
