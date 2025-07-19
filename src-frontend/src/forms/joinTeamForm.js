import React, {useEffect, useState} from "react";
import DynamicModal from "./dynamicModal";
import DynamicForm from "./dynamicForms";
import {useGetUserByIdQuery, useGetUsersQuery, usersApi, useUpdateUserMutation} from "../utils/reducers/usersSlice";
import {useDispatch} from "react-redux";
import {useJoinCompetitionMutation, useJoinTeamMutation} from "../utils/reducers/joinSlice";
import {useLocation, useNavigate} from "react-router-dom";
import {
    competitionsApi, useAddCompetitionMutation, useDeleteCompetitionMutation,
    useGetCompetitionByIdQuery,
    useUpdateCompetitionMutation
} from "../utils/reducers/competitionsSlice";
import {useAddTeamMutation, useDeleteTeamMutation, useGetTeamsQuery} from "../utils/reducers/teamsSlice";
import {PlusIcon, UsersRound, Trash2} from "lucide-react";
import {BeatLoader} from "react-spinners";
import {DeleteButton, Modal, SaveButton, SingleForm} from "./basicComponents";


export default function JoinTeamForm({setModalState, competition, join_code = null}) {

    const [joinTeam, {
        data: joinData,
        error: joinError,
        isLoading: joinIsLoading,
        isSuccess: joinIsSuccess
    }] = useJoinTeamMutation();
    const {
        data: teams,
        refetch: teamsRefetch,
        error: teamsError,
        isLoading: teamsLoading,
        isSuccess: teamsIsSuccess,
        isFetching: teamsIsFetching,
    } = useGetTeamsQuery();
    const [createTeam, {
        data: createData,
        error: createError,
        isLoading: createIsLoading,
        isSuccess: createIsSuccess
    }] = useAddTeamMutation();
    const [deleteTeam, {
        error: deleteError,
        isLoading: deleteIsLoading,
        isSuccess: deleteIsSuccess
    }] = useDeleteTeamMutation();
    //const filteredTeams = team?.filter(item => item.competition === competition.id);

    const {
        data: users,
        error: usersError,
        isLoading: usersIsLoading,
        isSuccess: usersIsSuccess
    } = useGetUsersQuery();

    const [filteredTeams, setFilteredTeams] = useState([]);

    useEffect(() => {
        if (teamsIsSuccess || usersIsSuccess) {
            let tmpTeams = [];
            for (const team of teams) {
                if (team.competition === competition.id) {
                    tmpTeams.push({
                        'name': team.name,
                        'id': team.id,
                        'user': team.user.map(user => users.find(userItem => userItem.id === user)),
                        'my': team.user.some(user => users.find(userItem => userItem.id === user).my),
                    });
                }
            }
            setFilteredTeams(tmpTeams);
        }
    }, [teams, users])

    useEffect(() => {
        if (createIsSuccess) {
            joinTeam(createData.id);
            teamsRefetch();
        }
    }, [createIsSuccess])

    function handleSubmit(e) {
        e.preventDefault();
        if (!(createIsLoading || joinIsLoading || teamsLoading)) {
            createTeam({competition: competition.id, name: e.target.teamName.value});
        }
    }

    function handleTeamChange(team_id) {
        joinTeam(team_id);
        teamsRefetch();
    }

    function handleTeamDelete(team_id) {
        deleteTeam(team_id);
        teamsRefetch();
    }


    return (
        <DynamicModal setModalState={setModalState}>
            <div className="flex items-center justify-center w-full">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl px-8 pt-6 pb-8 mb-4 ml-2 space-y-4 p-4">

                    {filteredTeams.map((team, index) => (
                        <div key={"team" + index} className="p-4">
                            <div className="flex justify-between items-center mb-2 border-b border-t py-2">
                                <h2 className="text-lg font-bold mr-auto">{team.name}</h2>
                                {(joinIsLoading || createIsLoading || teamsLoading || teamsIsFetching) ? (
                                    <BeatLoader color="rgb(209 213 219)"/>
                                ) : ((!team.my) ? (
                                            <>
                                                {((team.user.length === 0) ? (
                                                    <button onClick={() => handleTeamDelete(team.id)}
                                                            className="flex items-center gap-2 px-4 py-2 h-9 mr-2 bg-gray-100 rounded-full hover:bg-gray-300 transition">
                                                        <Trash2 className="w-3 h-3"/>
                                                    </button>
                                                ) : null)}
                                                <button onClick={() => handleTeamChange(team.id)}
                                                        className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full hover:bg-gray-300 transition">
                                                    <UsersRound className="w-3 h-3"/>
                                                    <span className="text-sm break-keep">Join Team</span>
                                                </button>
                                            </>
                                        )
                                        : <div className="text-sm pr-4">My Team</div>
                                )}
                            </div>
                            <ul className="list-disc list-inside text-gray-700">
                                {team.user.map((user, userindex) => (
                                    <li key={"teamuser" + userindex} className="py-0.5">{user.username}</li>
                                ))}
                            </ul>
                        </div>
                    ))}

                    <div className="p-4">
                        <h2 className="text-lg font-bold mb-2 border-b border-t py-2 mb-3">Create New Team</h2>
                        <form onSubmit={handleSubmit} className="flex items-center space-x-2">
                            <input
                                type="text"
                                name="teamName"
                                placeholder="Enter team name"
                                required={true}
                                disabled={createIsLoading || joinIsLoading || teamsLoading}
                                className="flex-1 border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                            />
                            {(joinIsLoading || createIsLoading || teamsLoading || teamsIsFetching) ? (
                                <BeatLoader color="rgb(209 213 219)"/>
                            ) : (
                                <button type="button" type="submit"
                                        disabled={createIsLoading || joinIsLoading || teamsLoading}
                                        className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full hover:bg-gray-300 transition">
                                    <PlusIcon className="w-3 h-3"/>
                                    <span className="text-sm break-keep">Create & Join</span>
                                </button>
                            )}
                        </form>
                    </div>


                    <p className="text-xs text-center italic text-gray-500">
                        <b>Note:</b> Team changes can take 10 minutes<br/>to reflect on the competition stats page.
                    </p>


                </div>


            </div>

        </DynamicModal>
    )
}
