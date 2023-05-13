#include "CommandDefinition.h"

#include "QmSkinSetWeights.h"
#include "QmMeshSetVertexColors.h"
#include "QmMeshSetNormals.h"
#include "QmMeshEditor.h"

namespace {
	std::vector<CommandCreation> commands_ = {
		{ QmSkinSetWeights::Name(), QmSkinSetWeights::Creator },
		{ QmMeshSetVertexColors::Name(), QmMeshSetVertexColors::Creator },
		{ QmMeshSetNormals::Name(), QmMeshSetNormals::Creator },
		{ QmMeshEditor::Name(), QmMeshEditor::Creator },
	};
}

const std::vector<CommandCreation>& ListCommands() {
	return commands_;
}
