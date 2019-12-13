from .Proposer import *

from .Utilities import *

from .CopyProposer import CopyProposer
copy_proposal = CopyProposer().proposal_content

from .DeleteProposer import DeleteProposer
delete_proposal = DeleteProposer().proposal_content

from .InsertProposer import InsertProposer
insert_proposal = InsertProposer().proposal_content

from .InsertDeleteProposer import InsertDeleteProposer
insert_delete_proposal = InsertDeleteProposer().proposal_content

from .MixtureProposer import MixtureProposer

from .RegenerationProposer import RegenerationProposer
regeneration_proposal = RegenerationProposer().proposal_content

from .InsertDeleteRegenerationProposer import InsertDeleteRegenerationProposer
IDR_proposal = InsertDeleteRegenerationProposer().proposal_content