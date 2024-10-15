from django.shortcuts import render, get_object_or_404, redirect
from collaboration_group.models import CollaborationGroup
from collaboration_member.models import GroupMember
from user.models import User

def manage_group(request, group_id):
    group = get_object_or_404(CollaborationGroup, pk=group_id)
    members = GroupMember.objects.filter(group=group)
    
    # Exclude users already in the group from the dropdown
    all_users = User.objects.exclude(id__in=[m.user.id for m in members])
    
    if request.method == 'POST' and 'add_member' in request.POST:
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        
        # Add the user to the group if not already a member
        if not GroupMember.objects.filter(group=group, user=user).exists():
            GroupMember.objects.create(group=group, user=user)
        
        return redirect('collaboration_group:manage_group', group_id=group.id)
    
    return render(request, 'manage_group.html', {
        'group': group,
        'members': members,
        'all_users': all_users,
    })

def remove_member(request, group_id, member_id):
    member = get_object_or_404(GroupMember, pk=member_id, group_id=group_id)
    member.delete()
    return redirect('collaboration_group:manage_group', group_id=group_id)