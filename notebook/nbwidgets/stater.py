from collections import defaultdict


class SectionViewerRuns:
    def __init__(self, section_viewer_runs):
        self.section_viewer = section_viewer

    def load_states(self):
        pass

    def dump_states(self):
        {
            "query_count": self.section_viewer.query_count,
            "word_count": self.section_viewer.word_count,
        }


"""
The data flow of Reviewer:
    1. [Human]: Outline (.md)
    2. [Agent]: Filled outline to sections, and dump (.json)
    3. [Viewer]: Create Section Viewer from outline/sections
    4. [Agent]: Section Viewer Runs
    5. [Viewer]: Dump Section Viewer Runs States (.json)
    6. [Viewer]: Load Section Viewer Runs States (.json)
    7. Go back to 3 (but this time use states to create section viewers), and repeat the loop.
"""


class SectionViewerRunStater:
    def __init__(self, viewer, viewer_type):
        self.viewer = viewer
        self.viewer_id = viewer.id
        self.viewer_type = viewer_type
        self.run_idx = -1
        self.states = defaultdict(lambda: defaultdict(list))

    def load_states(self):
        pass

    def update(self):
        self.run_idx = self.run_idx + 1
        viewer = self.viewer
        run_state_dict = {
            "run_idx": self.run_idx,
            "viewer_type": self.viewer_type,
            "level": viewer.section_node.level,
            "intro": viewer.section_node.intro,
            "query_count": viewer.query_count,
            "word_count": viewer.word_count,
            "response_content": viewer.response_content,
            "raw_output": viewer.output_chain.active_output(),
        }
        print(run_state_dict)
        self.states[self.viewer_id][self.viewer_type].append(run_state_dict)
